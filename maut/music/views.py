from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from datetime import datetime, timedelta
from models import Artist, Album, Track, Playlist, PlaylistTrack
from models import User, Genre, Year, UserPlaycount, UserRating
from models import add_track_from_tahoe
from models import last_tracks, newest_tracks, full_search
from models import random_tracks
from django.core.paginator import Paginator
import tagging
from django.db.models import Sum
from munin.helpers import muninview
import time
import csv
from cStringIO import StringIO


class rendered_with(object):
    def __init__(self, template_name):
        self.template_name = template_name

    def __call__(self, func):
        def rendered_func(request, *args, **kwargs):
            items = func(request, *args, **kwargs)
            if isinstance(items, dict):
                return render_to_response(
                    self.template_name,
                    items, context_instance=RequestContext(request))
            else:
                return items

        return rendered_func


@login_required
@rendered_with('music/index.html')
def index(request):
    return dict(last_tracks=last_tracks(request.user),
                newest_tracks=newest_tracks())


@login_required
@rendered_with('music/search.html')
def search(request):
    q = request.GET.get('q', '')
    if len(q) < 3:
        return HttpResponseRedirect("/")
    (tracks, artists, albums) = full_search(q)
    return dict(tracks=tracks, artists=artists, albums=albums)


@login_required
@rendered_with('music/artist.html')
def artist(request, id):
    artist = get_object_or_404(Artist, id=id)
    return dict(artist=artist)


@login_required
@rendered_with('music/album.html')
def album(request, id):
    album = get_object_or_404(Album, id=id)
    return dict(album=album,
                user_playlists=Playlist.objects.filter(owner=request.user))


@login_required
@rendered_with('music/track.html')
def track(request, id):
    track = get_object_or_404(Track, id=id)
    return dict(track=track,
                user_playlists=Playlist.objects.filter(owner=request.user))


@login_required
def add_track_to_playlist(request, id):
    track = get_object_or_404(Track, id=id)
    if request.method == "POST":
        playlist = get_object_or_404(Playlist, id=request.POST['playlist'])
        PlaylistTrack.objects.create(playlist=playlist, track=track,
                                     note=request.POST.get('note', ''))
    return HttpResponseRedirect(track.get_absolute_url())


@login_required
def add_album_to_playlist(request, id):
    album = get_object_or_404(Album, id=id)

    if request.method == "POST":
        playlist = get_object_or_404(Playlist, id=request.POST['playlist'])
        for track in album.track_set.all():
            PlaylistTrack.objects.create(playlist=playlist, track=track,
                                         note=request.POST.get('note', ''))
    return HttpResponseRedirect(album.get_absolute_url())


def playlist_playlist(request, id):
    playlist = get_object_or_404(Playlist, id=id)
    parts = ["""<?xml version="1.0" encoding="UTF-8"?>
    <playlist version="0" xmlns = "http://xspf.org/ns/0/">
    <trackList>"""]
    for pt in playlist.playlisttrack_set.all():
        if not pt.track.filetype == 1:
            continue
        parts.append("""<track>
        <location>%s</location>
        <annotation>%s [%s]</annotation>
        </track>""" % (pt.track.play(), pt.track.title, pt.track.artist.name))

    parts.append("""</trackList></playlist>""")
    return HttpResponse("".join(parts))


def track_playlist(self, id):
    track = get_object_or_404(Track, id=id)
    return HttpResponse("""<?xml version="1.0" encoding="UTF-8"?>
    <playlist version="0" xmlns = "http://xspf.org/ns/0/">
    <trackList>
    <track>
    <location>%s</location>
    <annotation>%s</annotation>
    </track>
    </trackList>
    </playlist>""" % (track.play(), track.title))


def album_playlist(request, id):
    album = get_object_or_404(Album, id=id)
    parts = ["""<?xml version="1.0" encoding="UTF-8"?>
    <playlist version="0" xmlns = "http://xspf.org/ns/0/">
    <trackList>"""]
    for track in album.track_set.all():
        if not track.filetype == 1:
            continue
        parts.append("""<track>
        <location>%s</location>
        <annotation>%s</annotation>
        </track>""" % (track.play(), track.title))

    parts.append("""</trackList></playlist>""")
    return HttpResponse("".join(parts))


def album_m3u(request, id):
    album = get_object_or_404(Album, id=id)
    output = "#EXTM3U\r\n" + "\r\n".join(
        [track.extended_m3u() for track in album.track_set.all()])
    return HttpResponse(output, mimetype="audio/x-mpegurl")


def album_play_m3u(request, id):
    album = get_object_or_404(Album, id=id)
    output = "#EXTM3U\r\n" + "\r\n".join(
        ["""#EXTINF:123,%s - %s
http://music.thraxil.org/track/%d/played/""" % (
        track.artist.name, track.title, track.id
    ) for track in album.track_set.all()])
    return HttpResponse(output, mimetype="audio/x-mpegurl")


@login_required
def rate_track(request, id):
    track = get_object_or_404(Track, id=id)
    rating = request.POST.get('rating', '0')
    track.rate(request.user, rating)
    return HttpResponse("ok")


def add_from_tahoe(request):
    if request.method != "POST":
        return HttpResponse(status=200, content="")
    add_track_from_tahoe(cap=request.POST['cap'],
                         artist=request.POST['artist'],
                         album=request.POST['album'],
                         title=request.POST['title'],
                         filename=request.POST.get("filename", ""),
                         year=request.POST.get('year', '0000'),
                         track=request.POST.get('track', '0'),
                         genre=request.POST.get('genre', 'Unknown'),
                         length=request.POST.get("length", "0"),
                         samplerate=request.POST.get("samplerate", "0"),
                         bitrate=request.POST.get("bitrate", "0"),
                         filesize=request.POST.get("filesize", "0"))
    return HttpResponse(status=200, content="ok")


def random_playlist(request):
    """ playlist of 50 random tracks of rating 8 or better """
    if request.user.is_anonymous():
        user = get_object_or_404(User, username='anp8')
    else:
        user = request.user
    tracks = list(random_tracks(user, 50))
    output = "#EXTM3U\r\n" + "\r\n".join(["""#EXTINF:123,%s - %s
http://music.thraxil.org/track/%d/played/""" % (
        track.artist.name, track.title, track.id
    ) for track in tracks])
    return HttpResponse(output, mimetype="audio/x-mpegurl")


@login_required
@rendered_with('music/rating.html')
def rating(request, rating):
    paginator = Paginator(
        Track.objects.filter(
            userrating__user=request.user,
            userrating__rating=rating).order_by(
                'artist__name', 'album__name', 'track', 'createdate'),
        100)

    try:
        page = int(request.GET.get('page',  '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (paginator.EmptyPage, paginator.InvalidPage):
        tracks = paginator.page(paginator.num_pages)

    return dict(tracks=tracks)


def rating_csv(request, rating):
    user = User.objects.get(username='anp8')
    r = Track.objects.filter(
        userrating__user=user,
        userrating__rating=rating)
    s = StringIO()
    csv_output = csv.writer(s)
#    csv_output.writeheader(["url","artist","album","track","title"])
    for t in r:
        csv_output.writerow(
            [
                t.play(local=True),
                t.artist.name.encode('utf-8'),
                t.album.name.encode('utf-8'),
                t.track,
                t.title.encode('utf-8')
            ])

    response = HttpResponse(s.getvalue(), mimetype="text/csv")
    response["Content-Disposition"] = (
        "attachment; filename=rating%d.csv" % int(rating))
    return response


@login_required
def rating_m3u(request, rating):
    tracks = Track.objects.filter(
        userrating__user=request.user,
        userrating__rating=rating).order_by(
            'artist__name', 'album__name', 'track', 'createdate')
    output = "#EXTM3U\r\n" + "\r\n".join(
        [track.extended_m3u() for track in tracks]
    )
    return HttpResponse(output, mimetype="audio/x-mpegurl")


def rating_play_m3u(request, rating):
    user = User.objects.get(username='anp8')
    tracks = Track.objects.filter(
        userrating__user=user,
        userrating__rating=rating).order_by(
            'artist__name', 'album__name', 'track', 'createdate')
    output = "#EXTM3U\r\n" + "\r\n".join(["""#EXTINF:123,%s - %s
http://music.thraxil.org/track/%d/played/""" % (
        track.artist.name, track.title, track.id
    ) for track in tracks])
    return HttpResponse(output, mimetype="audio/x-mpegurl")


def played_track(request, id):
    user = User.objects.get(username='anp8')
    track = get_object_or_404(Track, id=id)
    track.played(user)
    return HttpResponseRedirect(track.play(local=True))


@login_required
@rendered_with('music/ratings.html')
def ratings(request):
    data = []
    for r in range(11):
        tc = Track.objects.filter(userrating__user=request.user,
                                  userrating__rating=r).count()
        data.append(dict(rating=r, count=tc))
    data.reverse()
    return dict(ratings=data)


@login_required
@rendered_with('music/genres.html')
def genres(request):
    data = []
    for g in Genre.objects.all().order_by('name'):
        tc = Track.objects.filter(genre=g).count()
        data.append(dict(genre=g, count=tc))
    return dict(genres=data)


@login_required
@rendered_with('music/genre.html')
def genre(request, genre):
    g = get_object_or_404(Genre, id=genre)
    paginator = Paginator(
        Track.objects.filter(genre=g).order_by(
            'artist__name', 'album__name', 'track', 'createdate'
        ), 100)

    try:
        page = int(request.GET.get('page',  '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (paginator.EmptyPage,  paginator.InvalidPage):
        tracks = paginator.page(paginator.num_pages)
    return dict(genre=g, tracks=tracks)


@login_required
@rendered_with('music/years.html')
def years(request):
    data = []
    for y in Year.objects.all().order_by('name'):
        tc = Track.objects.filter(year=y).count()
        data.append(dict(year=y, count=tc))
    data.reverse()
    return dict(years=data)


@login_required
@rendered_with('music/year.html')
def year(request, year):
    y = get_object_or_404(Year, id=year)
    paginator = Paginator(
        Track.objects.filter(year=y).order_by(
            'artist__name', 'album__name', 'track', 'createdate'
        ), 100)

    try:
        page = int(request.GET.get('page',  '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (paginator.EmptyPage, paginator.InvalidPage):
        tracks = paginator.page(paginator.num_pages)
    return dict(year=y, tracks=tracks)


@login_required
@rendered_with('music/yeartop.html')
def yeartop(request):
    paginator = Paginator(
        Track.objects.filter(
            userrating__user=request.user,
            userrating__rating__gt=8, year__name=2012
        ).order_by(
            'artist__name', 'album__name', 'track', 'createdate'), 100)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (paginator.EmptyPage, paginator.InvalidPage):
        tracks = paginator.page(paginator.num_pages)
    return dict(tracks=tracks)


@login_required
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
        if request.GET.get("rating%d" % r, ''):
            ratings.append(r)
    if len(ratings) > 0:
        alltracks = alltracks.filter(userrating__user=request.user,
                                     userrating__rating__in=ratings)

    paginator = Paginator(
        alltracks.order_by(
            'artist__name', 'album__name', 'track', 'createdate'), 100)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (paginator.EmptyPage, paginator.InvalidPage):
        tracks = paginator.page(paginator.num_pages)

    allyears = []
    years = [int(y) for y in years]
    for year in Year.objects.all().order_by('name'):
        selected = False
        if year.id in years:
            selected = True
        allyears.append(dict(
            year=year,
            isselected=selected))

    params = dict()
    for k, v in request.GET.items():
        params[k] = v
    params.update(
        dict(
            tracks=tracks,
            years=allyears))
    return params


@login_required
def merge_genre(request, genre):
    g = get_object_or_404(Genre, id=genre)
    ng = get_object_or_404(Genre, id=request.POST['newgenre'])

    for t in g.track_set.all():
        t.genre = ng
        t.save()
    g.delete()
    return HttpResponseRedirect(ng.get_absolute_url())


@login_required
def merge_year(request, year):
    g = get_object_or_404(Year, id=year)
    ng = get_object_or_404(Year, id=request.POST['newyear'])

    for t in g.track_set.all():
        t.year = ng
        t.save()
    g.delete()
    return HttpResponseRedirect(ng.get_absolute_url())


@login_required
def update_track_tags(request, id):
    track = get_object_or_404(Track, id=id)
    track.tags = request.POST['tags']
    track.save()
    return HttpResponseRedirect(track.get_absolute_url())


@login_required
def track_tagup(request, id, tag):
    track = get_object_or_404(Track, id=id)
    t = get_object_or_404(tagging.models.Tag, name=tag)
    tagging.models.Tag.objects.add_tag(track.artist, "\"%s\"" % t.name)
    return HttpResponseRedirect(track.get_absolute_url())


@login_required
def update_artist_tags(request, id):
    artist = get_object_or_404(Artist, id=id)
    artist.tags = request.POST['tags']
    artist.save()
    return HttpResponseRedirect(artist.get_absolute_url())


@login_required
@rendered_with('music/tags.html')
def tags(request):
    return dict(tags=tagging.models.Tag.objects.all().order_by('name'))


@login_required
@rendered_with('music/tag.html')
def tag(request, tag):
    t = get_object_or_404(tagging.models.Tag, name=tag)
    paginator = Paginator(
        t.items.get_by_model(
            Track, [t]
        ).order_by('artist__name', 'album__name',
                   'track', 'createdate'), 100)

    try:
        page = int(request.GET.get('page',  '1'))
    except ValueError:
        page = 1

    try:
        tracks = paginator.page(page)
    except (paginator.EmptyPage, paginator.InvalidPage):
        tracks = paginator.page(paginator.num_pages)

    return dict(tag=t, tracks=tracks,
                artists=t.items.get_by_model(Artist, [t]).order_by('name'))


@login_required
@rendered_with('music/playlist_index.html')
def playlist_index(request):
    return dict(your_playlists=Playlist.objects.filter(owner=request.user),
                all_playlists=Playlist.objects.all())


@login_required
def create_playlist(request):
    if request.POST:
        name = request.POST.get('name', 'unnamed playlist')
        description = request.POST.get('description', '')
        owner = request.user
        Playlist.objects.create(name=name, owner=owner,
                                description=description)
    return HttpResponseRedirect("/playlist/")


@login_required
@rendered_with('music/playlist.html')
def playlist(request, id):
    playlist = get_object_or_404(Playlist, id=id)
    return dict(playlist=playlist)


@login_required
def remove_track_from_playlist(request, id):
    pt = get_object_or_404(PlaylistTrack, id=id)
    playlist = pt.playlist
    pt.delete()
    return HttpResponseRedirect(playlist.get_absolute_url())


@muninview(config="""graph_title Track Count
graph_vlabel tracks
graph_category Music""")
def track_count(request):
    return [("tracks", Track.objects.count())]


@muninview(config="""graph_title Hourly Play Count
graph_vlabel plays
graph_category Music""")
def hourly_plays(request, username):
    u = get_object_or_404(User, username=username)
    hour_ago = datetime.now() - timedelta(hours=1)
    accessdate = int(time.mktime(hour_ago.timetuple()))
    return [("plays",
             UserPlaycount.objects.filter(
                 user=u, accessdate__gt=accessdate).count())]


@muninview(config="""graph_title Unrated Tracks
graph_vlabel tracks
graph_category Music""")
def unrated_count(request, username):
    u = get_object_or_404(User, username=username)
    return [("tracks", UserRating.objects.filter(user=u, rating=0).count())]


@muninview(config="""graph_title Total Plays
graph_vlabel plays
graph_category Music""")
def total_plays(request, username):
    u = get_object_or_404(User, username=username)
    return [("tracks",
             UserPlaycount.objects.filter(
                 user=u
             ).aggregate(Sum("playcounter"))['playcounter__sum'])]