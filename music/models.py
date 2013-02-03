from django.db import models
import datetime
import time
import urllib
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import FLAC
import urllib2
import tagging
import thread
from django.contrib.auth.models import User
from restclient import GET, POST
from hashlib import md5


def md5hash(string):
    return md5(string).hexdigest()

TAHOE_BASE = "http://tahoe.ccnmtl.columbia.edu/"
LOCAL_TAHOE_BASE = "http://localhost:3456/"


def last_played_track(user):
    return Track.objects.filter(
        userplaycount__user=user).order_by("-userplaycount__accessdate")[0]


def sort_normalize_name(name):
    name = name.lower()
    if name.startswith('the '):
        name = name[4:]
    return name


def all_artists():
    """ return all artists sorted by name (normalized) """
    artists = list(Artist.objects.all())
    decorated = [(sort_normalize_name(a.name), a) for a in artists]
    decorated.sort(lambda a, b: cmp(a[0], b[0]))
    return [artist for name, artist in decorated]


def albumsort(a, b):
    if a.discnumber == b.discnumber:
        return cmp(a.track, b.track)
    else:
        return cmp(a.discnumber, b.discnumber)


def get_newest_track():
    return Track.objects.all().order_by("-modifydate")[0]


def add_track_from_tahoe(cap, filename="", artist="Unknown",
                         album="Unknown", title="Unknown",
                         modifydate=None,  year='0000',
                         track='0', genre='Unknown', length="0",
                         samplerate="0", bitrate="0", filesize="0"):
    if not filename.endswith(".mp3") or filename.endswith(".ogg"):
        return
    r = Track.objects.filter(url=cap)
    if r.count() > 0:
        # already in there
        return

    artist = get_or_create_artist(artist)
    album = get_or_create_album(album, artist)
    year = get_or_create_year(year)
    if '/' in track:
        track = track.split('/')[0]
        track = int(track)
    genre = get_or_create_genre(genre)
    modifydate = int(time.mktime(datetime.datetime.now().timetuple()))
    createdate = modifydate
    composer = Composer.objects.get(name='')
    comment = ""
    filetype = 1
    if filename.lower().endswith('ogg'):
        filetype = 2
    sampler = False
    bpm = 0.0
    discnumber = 0
    t = Track.objects.create(
        url=cap,
        createdate=int(createdate),
        modifydate=int(modifydate),
        album=album,
        artist=artist,
        composer=composer,
        genre=genre,
        title=title,
        year=year,
        comment=comment,
        track=int(track),
        discnumber=int(discnumber),
        bitrate=int(bitrate),
        length=int(length),
        samplerate=int(samplerate),
        filesize=int(filesize),
        filetype=int(filetype),
        sampler=sampler,
        bpm=bpm)
    for u in User.objects.all():
        # make rating/playcount objects for each user
        # this isn't going to scale well with many users :(
        t.userrating(u)
        t.userplaycount(u)


def get_or_create_artist(name):
    r = Artist.objects.filter(name__iexact=unicode(name))
    if r.count() == 0:
        return Artist.objects.create(name=name)
    else:
        return r[0]


def get_or_create_genre(name):
    r = Genre.objects.filter(name__iexact=unicode(name))
    if r.count() == 0:
        return Genre.objects.create(name=name)
    else:
        return r[0]


def get_or_create_year(name):
    r = Year.objects.filter(name=unicode(name))
    if r.count() == 0:
        return Year.objects.create(name=name)
    else:
        return r[0]


def get_or_create_album(name, artist):
    r = Album.objects.filter(name__iexact=unicode(name))
    if r.count() == 0:
        return Album.objects.create(name=name)
    else:
        # we need to make sure it's an album that's associated
        # with this artist
        for album in r:
            for track in album.track_set.all():
                if track.artist.id == artist.id:
                    # good enough
                    return album
            else:
                # no matches, so we make a fresh one
                # FIXME: doesn't deal well with compilations :(
                return Album.objects.create(name=name)


def get_id3_info_for_file(file):
    if file.lower().endswith('mp3'):
        audio = MP3(file)
    elif file.lower().endswith('ogg'):
        audio = OggVorbis(file)
    elif file.lower().endswith('flac'):
        audio = FLAC(file)
    return audio


class Genre(models.Model):
    name = models.CharField(max_length=256)

    class Meta:
        db_table = u'genre'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/genre/%d/" % self.id

    def all_others(self):
        return Genre.objects.all().exclude(id=self.id).order_by("name")


class Year(models.Model):
    name = models.TextField()

    class Meta:
        db_table = u'year'

    def get_absolute_url(self):
        return "/year/%d/" % self.id

    def all_others(self):
        return Year.objects.all().exclude(id=self.id).order_by("name")


class Images(models.Model):
    path = models.TextField()
    artist = models.TextField()
    album = models.TextField()

    class Meta:
        db_table = u'images'


class Lyrics(models.Model):
    url = models.TextField()
    lyrics = models.TextField()

    class Meta:
        db_table = u'lyrics'


class Album(models.Model):
    name = models.TextField()

    class Meta:
        db_table = u'album'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/album/%d/" % self.id

    def guess_artist(self):
        d = dict()
        artist = None
        for track in self.track_set.all():
            d[track.artist.id] = 1
            artist = track.artist
        if len(d.keys()) > 1:
            return None
        else:
            return artist


class Artist(models.Model):
    name = models.CharField(max_length=256)

    class Meta:
        db_table = u'artist'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/artist/%d/" % self.id

    def lastfm(self):
        return ("http://last.fm/music/"
                + urllib.quote_plus(self.name.encode('utf-8')))


try:
    tagging.register(Artist)
except tagging.AlreadyRegistered:
    pass


class Composer(models.Model):
    name = models.TextField()

    class Meta:
        db_table = u'composer'

    def __unicode__(self):
        return self.name


def full_search(q):
    title_tracks = Track.objects.filter(title__icontains=q)
    artists = Artist.objects.filter(name__icontains=q)
    albums = Album.objects.filter(name__icontains=q)
    return (title_tracks, artists, albums)


class Setting(models.Model):
    name = models.CharField(max_length=256)
    value = models.CharField(max_length=256)


def get_setting(name):
    return Setting.objects.get(name=name).value


def lastfm_handshake():
    password = open("/home/anders/.lastfm_password").read().strip()
    timestamp = int(time.time())
    auth_token = md5hash(md5hash(password) + str(timestamp))
    handshake_url = (
        "http://post.audioscrobbler.com/?hs=true&p=1.2&c="
        "tst&v=1.0&u=%s&t=%d&a=%s") % ("thraxil", timestamp, auth_token)
    try:
        handshake_response = GET(handshake_url)
    except:
        return ("BAD", "", "", "", 0)  # not responding
    if not handshake_response.startswith("OK"):
        return ("BAD", "", "", "", 0)  # something is wrong
    (status, session_id, now_playing_url,
     submission_url, _blah) = handshake_response.split("\n")
    return (status, session_id, now_playing_url, submission_url, timestamp)


class Scrobbler(object):
    def __init__(self, track):
        self.track = track

    def scrobble(self):
        if self.track.length < 30:
            # last.fm doesn't want to know about tracks shorter than
            # 30 seconds
            return
        (status, session_id, now_playing_url,
         submission_url, timestamp) = lastfm_handshake()
        if status != "OK":
            return  # something is wrong

        # now playing
        POST(now_playing_url,
             params=dict(s=session_id,
                         a=self.track.artist.name,
                         t=self.track.title,
                         b=self.track.album.name,
                         l=self.track.length,
                         n=self.track.track,
                         ),
             )

        def delayed_scrobble(track, timestamp):
            # we're supposed to wait 240 seconds or half the length
            # of the track before actually submitting
            delay = min(240, track.length / 2)
            time.sleep(delay)

            # just re-handshake since it could've been long enough that the
            # session expired
            password = open("/home/anders/.lastfm_password").read().strip()
            newtimestamp = int(time.time())
            auth_token = md5hash(md5hash(password) + str(newtimestamp))
            handshake_url = (
                "http://post.audioscrobbler.com/?hs=true&p=1.2&"
                "c=tst&v=1.0&u=%s&t=%d&a=%s") % (
                    "thraxil", newtimestamp, auth_token)
            handshake_response = GET(handshake_url)
            if not handshake_response.startswith("OK"):
                return  # something is wrong
            (status, session_id, now_playing_url,
             submission_url, _blah) = handshake_response.split("\n")

            POST(
                submission_url,
                params={
                    's': session_id,
                    'a[0]': track.artist.name,
                    't[0]': track.title,
                    'b[0]': track.album.name,
                    'i[0]': timestamp,
                    'o[0]': 'P',
                    'r[0]': 'L',
                    'm[0]': "",
                    'l[0]': track.length,
                    'n[0]': track.track
                }
            )
        thread.start_new_thread(delayed_scrobble, (self.track, timestamp))


class Track(models.Model):
    url = models.CharField(max_length=256)
    createdate = models.IntegerField()
    modifydate = models.IntegerField()
    album = models.ForeignKey(Album, db_column="album")
    artist = models.ForeignKey(Artist, db_column="artist")
    composer = models.ForeignKey(Composer, db_column="composer")
    genre = models.ForeignKey(Genre, db_column="genre")
    title = models.CharField(max_length=256)
    year = models.ForeignKey(Year, db_column="year")
    comment = models.TextField()
    track = models.DecimalField(max_digits=4, decimal_places=0)
    discnumber = models.IntegerField()
    bitrate = models.IntegerField()
    length = models.IntegerField()
    samplerate = models.IntegerField()
    filesize = models.IntegerField()
    filetype = models.IntegerField()
    sampler = models.BooleanField()
    bpm = models.FloatField()

    class Meta:
        db_table = u'tags'
        ordering = ('album__name', 'discnumber', 'track', 'title')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return "/track/%d/" % self.id

    def minutes(self):
        hours = self.length / 3600
        minutes = (self.length / 60) % 60
        seconds = self.length % 60
        if hours > 0:
            return "%02d:%02d:%02d" % (hours, minutes, seconds)
        else:
            return "%02d:%02d" % (minutes, seconds)

    def mb(self):
        mb = self.filesize / (1024.0 * 1024.0)
        return "%.02f" % mb

    def download(self):
        url = self.url
        fname = "file.mp3"
        if self.filetype != 1:
            fname = "file.ogg"
        url = TAHOE_BASE + "file/" + urllib2.quote(url) + "/@@named=" + fname
        return url

    def filename(self):
        # once it's in tahoe, we don't know the original
        # filename
        if self.filetype == 2:
            return "file.ogg"
        else:
            return "file.mp3"

    def created(self):
        return datetime.datetime.fromtimestamp(self.createdate)

    def userplaycount(self, user):
        return UserPlaycount.objects.get_or_create(
            user=user,
            track=self,
            defaults={'playcounter': 0, 'accessdate': 0})[0]

    def played(self, user):
        accessdate = int(time.mktime(datetime.datetime.now().timetuple()))
        up = self.userplaycount(user)
        up.playcounter = up.playcounter + 1
        up.accessdate = accessdate
        up.save()
        self.scrobble()

    def scrobble(self):
        Scrobbler(self).scrobble()

    def accessed(self, user):
        up = self.userplaycount(user)
        return datetime.datetime.fromtimestamp(up.accessdate)

    def userrating(self, user):
        return UserRating.objects.get_or_create(
            user=user, track=self, defaults={'rating': 0})[0]

    def rate(self, user, rating):
        ur = self.userrating(user)
        ur.rating = int(rating)
        ur.save()

    def is_mp3(self):
        return self.filetype == 1

    def play(self, local=False):
        url = self.url.encode('utf-8')
        fname = "file.mp3"
        if self.filetype != 1:
            fname = "file.ogg"
        if local:
            return (LOCAL_TAHOE_BASE + "file/" + urllib2.quote(url)
                    + "/@@named=" + fname)
        else:
            return (TAHOE_BASE + "file/" + urllib2.quote(url)
                    + "/@@named=" + fname)

    def extended_m3u(self):
        return """#EXTINF:123,%s - %s
%s""" % (self.artist.name, self.title, self.play())

try:
    tagging.register(Track)
except tagging.AlreadyRegistered:
    pass


class UserRating(models.Model):
    user = models.ForeignKey(User)
    track = models.ForeignKey(Track)
    rating = models.IntegerField(default=0)


class UserPlaycount(models.Model):
    user = models.ForeignKey(User)
    track = models.ForeignKey(Track)
    playcounter = models.IntegerField(default=0)
    accessdate = models.IntegerField()


class Playlist(models.Model):
    name = models.CharField(max_length=256)
    owner = models.ForeignKey(User)
    description = models.TextField(default="", blank=True, null=True)

    def get_absolute_url(self):
        return "/playlist/%d/" % self.id


class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(Playlist)
    track = models.ForeignKey(Track)
    note = models.TextField(default="", blank=True, null=True)

    class Meta:
        order_with_respect_to = 'playlist'


def last_tracks(user, limit=20, offset=0):
    return Track.objects.filter(
        userplaycount__user=user,
        userplaycount__playcounter__gt=0
    ).order_by("-userplaycount__accessdate")[offset:offset + limit]


def newest_tracks(limit=20, offset=0):
    return Track.objects.all().order_by('-createdate')[offset:offset + limit]


def unrated_tracks(user):
    tracks = Track.objects.filter(
        userrating__user=user,
        userrating__rating=0
    ).order_by('artist__name', 'album__name', 'track', 'createdate')
    return tracks


def random_tracks(user, num=50):
    tracks = Track.objects.filter(userrating__user=user,
                                  userrating__rating__gte=8).order_by('?')
    return tracks[:num]


def extract_tahoe_cap(url):
    parts = url.split("/")
    cap = parts[4].replace("%3A", ":")
    return cap


class RelatedArtists(models.Model):
    artist = models.TextField()
    suggestion = models.TextField()
    changedate = models.IntegerField()

    class Meta:
        db_table = u'related_artists'


# not sure what these are for
class Amazon(models.Model):
    asin = models.TextField()
    locale = models.TextField()
    filename = models.TextField()
    refetchdate = models.IntegerField()

    class Meta:
        db_table = u'amazon'
