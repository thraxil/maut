# Create your views here.
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from datetime import datetime
from django.template.defaultfilters import slugify
import simplejson
from models import *
from subprocess import Popen,PIPE
import os.path
import cStringIO
from tempfile import TemporaryFile
from django.core.paginator import Paginator
import random
import os

class rendered_with(object):
    def __init__(self, template_name):
        self.template_name = template_name

    def __call__(self, func):
        def rendered_func(request, *args, **kwargs):
            items = func(request, *args, **kwargs)
            if type(items) == type({}):
                return render_to_response(self.template_name, items, context_instance=RequestContext(request))
            else:
                return items

        return rendered_func

@login_required
@rendered_with('music/index.html')
def index(request):
    return dict(last_tracks=last_tracks(),
                newest_tracks=newest_tracks())

@login_required
@rendered_with('music/search.html')
def search(request):
    q = request.GET.get('q','')
    if len(q) < 3:
        return HttpResponseRedirect("/")
    (tracks,artists,albums) = full_search(q)
    return dict(tracks=tracks,artists=artists,albums=albums)

@login_required
@rendered_with('music/artist.html')
def artist(request,id):
    artist = get_object_or_404(Artist,id=id)
    return dict(artist=artist)

@login_required
@rendered_with('music/album.html')
def album(request,id):
    album = get_object_or_404(Album,id=id)
    return dict(album=album)

@login_required
@rendered_with('music/track.html')
def track(request,id):
    track = get_object_or_404(Track,id=id)
    return dict(track=track)

def track_playlist(self,id):
    track = get_object_or_404(Track,id=id)
    return HttpResponse("""<?xml version="1.0" encoding="UTF-8"?>
    <playlist version="0" xmlns = "http://xspf.org/ns/0/">
    <trackList>
    <track>
    <location>%s</location>
    <annotation>%s</annotation>
    </track>
    </trackList>
    </playlist>""" % (track.play(),track.title))

def album_playlist(request,id):
    album = get_object_or_404(Album,id=id)
    parts = ["""<?xml version="1.0" encoding="UTF-8"?>
    <playlist version="0" xmlns = "http://xspf.org/ns/0/">
    <trackList>"""]
    for track in album.track_set.all():
        if not track.filetype == 1:
            continue
        parts.append("""<track>
        <location>%s</location>
        <annotation>%s</annotation>
        </track>""" % (track.play(),track.title))

    parts.append("""</trackList></playlist>""")
    return HttpResponse("".join(parts))


def rate_track(request,id):
    track = get_object_or_404(Track,id=id)
    rating = request.POST.get('rating','0')
    track.rate(rating)
    return HttpResponse("ok")


def update(request):
    if request.method == "POST":
        track = get_current_playing_track()
        if track is None:
            return HttpResponse(status=200,content="")
        last_played = last_played_track()
        if track.id != last_played.id:
            track.played()
        return HttpResponse(status=200,content="")
    else:
        return HttpResponse(status=200,content="")

def rate_current(request,rating):
    if request.method == "POST":
        track = get_current_playing_track()
        if track is None:
            return HttpResponse(status=200,content="")
        track.rate(rating)
        return HttpResponse(status=200,content="")
    else:
        return HttpResponse(status=200,content="")

def updatedb(request):
    """ scan the music directory looking for new files """
    if request.method != "POST":
        return HttpResponse(status=200,content="")
    scan_for_new_files()
    return HttpResponse(status=200,content="")

def updatedir(request):
    """ scan a single directory looking for new files """
    if request.method != "POST":
        return HttpResponse(status=200,content="")
    scan_for_new_files(start_dir=request.POST['dir'],deep=True)
    return HttpResponse(status=200,content="")

def add_from_tahoe(request):
    if request.method != "POST":
        return HttpResponse(status=200,content="")
    add_track_from_tahoe(cap=request.POST['cap'],
                         artist=request.POST['artist'],
                         album=request.POST['album'],
                         title=request.POST['title'],
                         filename=request.POST.get("filename",""),
                         modifydate=request.POST.get("modifydate",""), 
                         year=request.POST.get('year','0000'),
                         track=request.POST.get('track','0'),
                         genre=request.POST.get('genre','Unknown'),
                         length=request.POST.get("length","0"),
                         samplerate=request.POST.get("samplerate","0"),
                         bitrate=request.POST.get("bitrate","0"),
                         filesize=request.POST.get("filesize","0"))
    return HttpResponse(status=200,content="ok")

def deep_updatedb(request):
    """ scan the music directory looking for new files """
    if request.method != "POST":
        return HttpResponse(status=200,content="")
    scan_for_new_files(deep=True,new_only=True)
    return HttpResponse(status=200,content="")


def queueunrated(request):
    if request.method != "POST":
        return HttpResponse(status=200,content="")
    unrated = unrated_tracks()
    for track in unrated:
        add_track_to_playlist(track)
    return HttpResponse(status=200,content="")

@rendered_with('music/rating.html')
def rating(request,rating):
    paginator = Paginator(Track.objects.filter(rating=rating).order_by('artist__name','album__name','track','createdate'), 100)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)

    return dict(tracks=tracks)

@rendered_with('music/ratings.html')
def ratings(request):
    data = []
    for r in range(11):
        tc = Track.objects.filter(rating=r).count()
        data.append(dict(rating=r,count=tc))
    data.reverse()
    return dict(ratings=data)

@rendered_with('music/genres.html')
def genres(request):
    data = []
    for g in Genre.objects.all().order_by('name'):
        tc = Track.objects.filter(genre=g).count()
        data.append(dict(genre=g,count=tc))
    return dict(genres=data)

@rendered_with('music/genre.html')
def genre(request,genre):
    g = get_object_or_404(Genre,id=genre)
    paginator = Paginator(Track.objects.filter(genre=g).order_by('artist__name','album__name','track','createdate'), 100)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)
    return dict(genre=g,tracks=tracks)

def load_ipod(request):
    # TODO: broken with tahoe
    IPOD = "/media/ipod/"
    try:
        os.makedirs(IPOD + "10")
    except:
        pass
    log = []
    for track in Track.objects.filter(rating=10):
        track.copy_to_ipod()
        log.append(track.ipod_filename())
    random.shuffle(log)
    playlist = open(IPOD + "10" + "/all.m3u","w")
    for line in log:
        try:
            playlist.write(line + "\n")
        except UnicodeEncodeError:
            pass
    playlist.close()
    return HttpResponse("ok")
