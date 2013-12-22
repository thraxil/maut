from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from models import Artist, Album, Track, Playlist, PlaylistTrack
from models import User, Genre, Year
from models import add_track_from_tahoe
from models import last_tracks, newest_tracks, full_search
from models import random_tracks
from django.core.paginator import Paginator
import tagging
import csv
from cStringIO import StringIO
from annoying.decorators import render_to


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class IndexView(LoggedInMixin, TemplateView):
    template_name = 'music/index.html'

    def get_context_data(self):
        return dict(last_tracks=last_tracks(self.request.user),
                    newest_tracks=newest_tracks())


class SearchView(LoggedInMixin, TemplateView):
    template_name = 'music/search.html'

    def get_context_data(self):
        q = self.request.GET.get('q', '')
        if len(q) < 3:
            return HttpResponseRedirect("/")
        (tracks, artists, albums) = full_search(q)
        return dict(tracks=tracks, artists=artists, albums=albums)


class ArtistView(LoggedInMixin, DetailView):
    template_name = 'music/artist.html'
    model = Artist
    context_object_name = 'artist'


@login_required
@render_to('music/album.html')
def album(request, id):
    album = get_object_or_404(Album, id=id)
    return dict(album=album,
                user_playlists=Playlist.objects.filter(owner=request.user))


@login_required
@render_to('music/track.html')
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
@render_to('music/rating.html')
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
@render_to('music/ratings.html')
def ratings(request):
    data = []
    for r in range(11):
        tc = Track.objects.filter(userrating__user=request.user,
                                  userrating__rating=r).count()
        data.append(dict(rating=r, count=tc))
    data.reverse()
    return dict(ratings=data)


@login_required
@render_to('music/genres.html')
def genres(request):
    data = []
    for g in Genre.objects.all().order_by('name'):
        tc = Track.objects.filter(genre=g).count()
        data.append(dict(genre=g, count=tc))
    return dict(genres=data)


@login_required
@render_to('music/genre.html')
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
@render_to('music/years.html')
def years(request):
    data = []
    for y in Year.objects.all().order_by('name'):
        tc = Track.objects.filter(year=y).count()
        data.append(dict(year=y, count=tc))
    data.reverse()
    return dict(years=data)


@login_required
@render_to('music/year.html')
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
@render_to('music/yeartop.html')
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


def build_ratings(get):
    ratings = []
    for r in range(11):
        if get.get("rating%d" % r, ''):
            ratings.append(r)
    return ratings


def get_page(request):
    try:
        return int(request.GET.get('page', '1'))
    except ValueError:
        return 1


def get_tracks(paginator, page):
    try:
        return paginator.page(page)
    except (paginator.EmptyPage, paginator.InvalidPage):
        return paginator.page(paginator.num_pages)


@login_required
@render_to('music/facet.html')
def facet(request):
    # available facets:
    # year
    # rating

    alltracks = Track.objects.all()
    years = request.GET.getlist('year')
    if len(years) > 0:
        alltracks = alltracks.filter(year__in=years)

    ratings = build_ratings(request.GET)
    if len(ratings) > 0:
        alltracks = alltracks.filter(userrating__user=request.user,
                                     userrating__rating__in=ratings)

    paginator = Paginator(
        alltracks.order_by(
            'artist__name', 'album__name', 'track', 'createdate'), 100)
    page = get_page(request)
    tracks = get_tracks(paginator, page)
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
@render_to('music/tags.html')
def tags(request):
    return dict(tags=tagging.models.Tag.objects.all().order_by('name'))


@login_required
@render_to('music/tag.html')
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


class PlaylistIndexView(LoggedInMixin, TemplateView):
    template_name = 'music/playlist_index.html'

    def get_context_data(self):
        return dict(
            your_playlists=Playlist.objects.filter(
                owner=self.request.user),
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
@render_to('music/playlist.html')
def playlist(request, id):
    playlist = get_object_or_404(Playlist, id=id)
    return dict(playlist=playlist)


@login_required
def remove_track_from_playlist(request, id):
    pt = get_object_or_404(PlaylistTrack, id=id)
    playlist = pt.playlist
    pt.delete()
    return HttpResponseRedirect(playlist.get_absolute_url())
