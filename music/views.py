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

@rendered_with('music/index.html')
def index(request):
    return dict(last_tracks=last_tracks(),
                newest_tracks=newest_tracks())

@rendered_with('music/unrated.html')
def unrated(request):
    return dict(unrated=unrated_tracks())

@rendered_with('music/search.html')
def search(request):
    q = request.GET.get('q','')
    if len(q) < 3:
        return HttpResponseRedirect("/")
    (tracks,artists,albums) = full_search(q)
    return dict(tracks=tracks,artists=artists,albums=albums)


@rendered_with('music/artist.html')
def artist(request,id):
    artist = get_object_or_404(Artist,id=id)
    return dict(artist=artist)

@rendered_with('music/album.html')
def album(request,id):
    album = get_object_or_404(Album,id=id)
    return dict(album=album)

@rendered_with('music/track.html')
def track(request,id):
    track = get_object_or_404(Track,id=id)
    return dict(track=track)

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

def queueunrated(request):
    if request.method != "POST":
        return HttpResponse(status=200,content="")
    unrated = unrated_tracks()
    for track in unrated:
        add_track_to_playlist(track)
    return HttpResponse(status=200,content="")
