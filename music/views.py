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
@rendered_with('music/unrated.html')
def unrated(request):
    return dict(unrated=unrated_tracks())

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
        if not track.url.lower().endswith('mp3'):
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

def deep_updatedb(request):
    """ scan the music directory looking for new files """
#    if request.method != "POST":
#        return HttpResponse(status=200,content="")
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
    paginator = Paginator(Track.objects.filter(rating=rating), 100)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)

    return dict(tracks=tracks)
