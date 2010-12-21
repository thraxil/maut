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
import tagging

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

def album_m3u(request,id):
    album = get_object_or_404(Album,id=id)
    output = "#EXTM3U\r\n" + "\r\n".join([track.extended_m3u() for track in album.track_set.all()])
    return HttpResponse(output,mimetype="audio/x-mpegurl")

def album_play_m3u(request,id):
    album = get_object_or_404(Album,id=id)
    output = "#EXTM3U\r\n" + "\r\n".join(["""#EXTINF:123,%s - %s
http://music.thraxil.org/track/%d/played/""" % (track.artist.name,track.title,track.id) for track in album.track_set.all()])
    return HttpResponse(output,mimetype="audio/x-mpegurl")

def rate_track(request,id):
    track = get_object_or_404(Track,id=id)
    rating = request.POST.get('rating','0')
    track.rate(request.user,rating)
    return HttpResponse("ok")

def rate_current(request,rating):
    if request.method == "POST":
        track = get_current_playing_track()
        if track is None:
            return HttpResponse(status=200,content="")
        track.rate(request.user,rating)
        return HttpResponse(status=200,content="")
    else:
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

def random_playlist(request):
    """ playlist of 50 random tracks of rating 8 or better """
    tracks = list(random_tracks(request.user,50))
    output = "#EXTM3U\r\n" + "\r\n".join(["""#EXTINF:123,%s - %s
http://music.thraxil.org/track/%d/played/""" % (track.artist.name,track.title,track.id) for track in tracks])
    return HttpResponse(output,mimetype="audio/x-mpegurl")

@rendered_with('music/rating.html')
def rating(request,rating):
    paginator = Paginator(Track.objects.filter(userrating__user=request.user,
                                               userrating__rating=rating).order_by('artist__name','album__name','track','createdate'), 100)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)

    return dict(tracks=tracks)

def rating_m3u(request,rating):
    tracks = Track.objects.filter(userrating__user=request.user,
                                  userrating__rating=rating).order_by('artist__name','album__name','track','createdate')
    output = "#EXTM3U\r\n" + "\r\n".join([track.extended_m3u() for track in tracks])
    return HttpResponse(output,mimetype="audio/x-mpegurl")

def rating_play_m3u(request,rating):
    tracks = Track.objects.filter(userrating__user=request.user,
                                  userrating__rating=rating).order_by('artist__name','album__name','track','createdate')
    output = "#EXTM3U\r\n" + "\r\n".join(["""#EXTINF:123,%s - %s
http://music.thraxil.org/track/%d/played/""" % (track.artist.name,track.title,track.id) for track in tracks])
    return HttpResponse(output,mimetype="audio/x-mpegurl")

def played_track(request,id):
    track = get_object_or_404(Track,id=id)
    track.played()
    return HttpResponseRedirect(track.play(local=True))

@rendered_with('music/ratings.html')
def ratings(request):
    data = []
    for r in range(11):
        tc = Track.objects.filter(userrating__user=request.user,
                                  userrating__rating=r).count()
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

@rendered_with('music/years.html')
def years(request):
    data = []
    for y in Year.objects.all().order_by('name'):
        tc = Track.objects.filter(year=y).count()
        data.append(dict(year=y,count=tc))
    data.reverse()
    return dict(years=data)

@rendered_with('music/year.html')
def year(request,year):
    y = get_object_or_404(Year,name=year)
    paginator = Paginator(Track.objects.filter(year=y).order_by('artist__name','album__name','track','createdate'), 100)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)
    return dict(year=y,tracks=tracks)

@rendered_with('music/yeartop.html')
def yeartop(request):
    paginator = Paginator(Track.objects.filter(userrating__user=request.user,
                                               userrating__rating__gt=8,year__name=2009).order_by('artist__name','album__name','track','createdate'), 100)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)
    return dict(tracks=tracks)

@rendered_with('music/facet.html')
def facet(request):
    # available facets:
    # year
    # rating

    alltracks = Track.objects.all()
    years = request.GET.getlist('year')
    if len(years) > 0:
        alltracks = alltracks.filter(year__in=years)

    ratings = []
    for r in range(11):
        if request.GET.get("rating%d" % r,''):
            ratings.append(r)
    if len(ratings) > 0:
        alltracks = alltracks.filter(userrating__user=request.user,
                                     userrating__rating__in=ratings)

    paginator = Paginator(alltracks.order_by('artist__name','album__name','track','createdate'), 100)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)

    allyears = []
    years = [int(y) for y in years]
    for year in Year.objects.all().order_by('name'):
        selected=False
        if year.id in years:
            selected=True
        allyears.append(dict(
                year=year,
                isselected=selected
                ))

    params = dict()
    for k,v in request.GET.items():
        params[k] = v
    params.update(dict(tracks=tracks,
                years=allyears))
    return params



def merge_genre(request,genre):
    g = get_object_or_404(Genre,id=genre)
    ng = get_object_or_404(Genre,id=request.POST['newgenre'])

    for t in g.track_set.all():
        t.genre = ng
        t.save()
    g.delete()
    return HttpResponseRedirect(ng.get_absolute_url())

def update_track_tags(request,id):
    track = get_object_or_404(Track,id=id)
    track.tags = request.POST['tags']
    track.save()
    return HttpResponseRedirect(track.get_absolute_url())

def track_tagup(request,id,tag):
    track = get_object_or_404(Track,id=id)
    t = get_object_or_404(tagging.models.Tag,name=tag)
    tagging.models.Tag.objects.add_tag(track.artist,"\"%s\"" % t.name)
    return HttpResponseRedirect(track.get_absolute_url())

def update_artist_tags(request,id):
    artist = get_object_or_404(Artist,id=id)
    artist.tags = request.POST['tags']
    artist.save()
    return HttpResponseRedirect(artist.get_absolute_url())


@rendered_with('music/tags.html')
def tags(request):
    return dict(tags=tagging.models.Tag.objects.all().order_by('name'))

@rendered_with('music/tag.html')
def tag(request,tag):
    t = get_object_or_404(tagging.models.Tag,name=tag)
    paginator = Paginator(t.items.get_by_model(Track,[t]).order_by('artist__name','album__name','track','createdate'), 100)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (EmptyPage, InvalidPage):
        tracks = paginator.page(paginator.num_pages)


    return dict(tag=t,tracks=tracks,
                artists=t.items.get_by_model(Artist,[t]).order_by('name'))

