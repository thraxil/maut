from django.db import models
from django.contrib import admin
import datetime
import time
import urllib
from subprocess import Popen,PIPE
import os.path
import cStringIO
from tempfile import TemporaryFile
from stat import ST_SIZE,ST_MTIME
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import FLAC

def last_played_track():
    s = Statistic.objects.all().order_by("-accessdate")[0]
    return Track.objects.get(url=s.url)

def sort_normalize_name(name):
    name = name.lower()
    if name.startswith('the '):
        name = name[4:]
    return name

def all_artists():
    """ return all artists sorted by name (normalized) """
    artists = list(Artist.objects.all())
    decorated = [(sort_normalize_name(a.name),a) for a in artists]
    decorated.sort(lambda a,b: cmp(a[0],b[0]))
    return [artist for name,artist in decorated]

def albumsort(a,b):
    if a.discnumber == b.discnumber:
        return cmp(a.track,b.track)
    else:
        return cmp(a.discnumber,b.discnumber)

def get_newest_track():
    return Track.objects.all().order_by("-modifydate")[0]

def scan_for_new_files():
    ROOT = "/home/anders/MyMusic/"
    newest = get_newest_track()
    for (root,dirs,files) in os.walk(ROOT):
        if dirs == []:
            for f in files:
                fl = f.lower()
                if not fl.endswith('mp3') or fl.endswith('ogg'):
                    continue
                if os.stat(os.path.join(root,f))[ST_MTIME] < newest.modifydate:
                    continue
                existing_track = None
                try:
                    existing_track = Track.objects.get(url="." + os.path.join(root,f))
                    # already exists
                except Track.DoesNotExist:
                    pass
                data = get_id3_info_for_file(os.path.join(root,f))
                artist = get_or_create_artist(unicode(data.get('TPE1','Unknown')))
                title = unicode(data.get('TIT2','Unknown'))
                album = get_or_create_album(unicode(data.get('TALB','Unknown')),artist)
                year = get_or_create_year(unicode(data.get('TDRC','0000')))
                track = unicode(data.get('TRCK','0'))
                if '/' in track:
                    track = track.split('/')[0]
                track = int(track)
                genre = get_or_create_genre(unicode(data.get('TCON','Unknown')))
                modifydate = os.stat(os.path.join(root,f))[ST_MTIME]
                createdate = modifydate
                composer = Composer.objects.get(name='')
                comment = ""
                length = data.info.length
                samplerate = data.info.sample_rate
                bitrate = data.info.bitrate
                filesize = os.stat(os.path.join(root,f))[ST_SIZE]
                filetype = 1
                if f.lower().endswith('ogg'):
                    filetype = 2
                sampler = False
                bpm = 0.0
                discnumber = 0
                if existing_track is None:
                    # new track
                    t = Track.objects.create(
                        url = "." + os.path.join(root,f),
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
                else:
                    # update existing
                    et = existing_track
                    et.url = "." + os.path.join(root,f),
                    et.createdate=int(createdate)
                    et.modifydate=int(modifydate)
                    et.album=album
                    et.artist=artist
                    et.composer=composer
                    et.genre=genre
                    et.title=title
                    et.year=year
                    et.comment=comment
                    et.track=int(track)
                    et.discnumber=int(discnumber)
                    et.bitrate=int(bitrate)
                    et.length=int(length)
                    et.samplerate=int(samplerate)
                    et.filesize=int(filesize)
                    et.filetype=int(filetype)
                    et.sampler=sampler
                    et.bpm=bpm
                    et.save()
                    

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


def get_or_create_album(name,artist):
    r = Album.objects.filter(name__iexact=unicode(name))
    if r.count() == 0:
        return Album.objects.create(name=name)
    else:
        # we need to make sure it's an album that's associated
        # with this artist 
        for album in r:
            for track in album.track_set.all():
                if track.artist == artist:
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

class Year(models.Model):
    name = models.TextField()
    class Meta:
        db_table = u'year'

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

class Statistic(models.Model):
    url = models.TextField()
    createdate = models.IntegerField()
    accessdate = models.IntegerField()
    percentage = models.FloatField()
    rating = models.IntegerField()
    playcounter = models.IntegerField()
    deleted = models.BooleanField()
    class Meta:
        db_table = u'statistics'

    def created(self):
        return datetime.datetime.fromtimestamp(self.createdate)

    def accessed(self):
        return datetime.datetime.fromtimestamp(self.accessdate)

    def track(self):
        return Track.objects.get(url=self.url)


class Label(models.Model):
    name = models.TextField()
    type = models.IntegerField()
    class Meta:
        db_table = u'labels'

    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return "/label/%d/" % self.id


class TrackLabel(models.Model):
    url = models.TextField()
    labelid = models.ForeignKey(Label, db_column='labelid')
    class Meta:
        db_table = u'tags_labels'

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
        return "http://last.fm/music/" + urllib.quote_plus(self.name.encode('utf-8'))

class Composer(models.Model):
    name = models.TextField()
    class Meta:
        db_table = u'composer'
    def __unicode__(self):
        return self.name

class Track(models.Model):
    url = models.CharField(max_length=256)
    createdate = models.IntegerField()
    modifydate = models.IntegerField()
    album = models.ForeignKey(Album,db_column="album")
    artist = models.ForeignKey(Artist,db_column="artist")
    composer = models.ForeignKey(Composer,db_column="composer")
    genre = models.ForeignKey(Genre,db_column="genre")
    title = models.CharField(max_length=256)
    year = models.ForeignKey(Year,db_column="year")
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
        ordering = ('album__name', 'discnumber','track','title')


    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        return "/track/%d/" % self.id

    def minutes(self):
        hours = self.length / 3600
        minutes = (self.length / 60) % 60
        seconds = self.length % 60
        if hours > 0:
            return "%02d:%02d:%02d" % (hours,minutes,seconds)
        else:
            return "%02d:%02d" % (minutes,seconds)

    def mb(self):
        mb = self.filesize / (1024.0 * 1024.0)
        return "%.02f" % mb

    def download(self):
        url = self.url
        if url.startswith("./home/anders/MyMusic/"):
            url = url.replace("./home/anders/MyMusic/","http://behemoth.ccnmtl.columbia.edu/music/")
        return url
    def relative_path(self):
        url = self.url
        if url.startswith("./home/anders/MyMusic/"):
            url = url.replace("./home/anders/MyMusic/","")
        return url

    def filename(self):
        return self.url.split('/')[-1]

    def statistics(self):
        try:
            return Statistic.objects.get(url=self.url)
        except Statistic.DoesNotExist:
            return Statistic.objects.create(
                url=self.url,
                playcounter=0,
                percentage=0,
                rating=0,
                deleted=False,
                createdate=self.createdate,
                accessdate=self.modifydate)
      
    def played(self):
        accessdate = int(time.mktime(datetime.datetime.now().timetuple()))
        s = self.statistics()
        s.playcounter = s.playcounter + 1
        s.accessdate = accessdate
        s.save()

    def rate(self,rating):
        s = self.statistics()
        s.rating = int(rating)
        s.save()

def last_tracks(limit=20,offset=0):
    stats = Statistic.objects.all().order_by("-accessdate")[offset:offset+limit]
    return [Track.objects.get(url=s.url) for s in stats]

def newest_tracks(limit=20,offset=0):
    return Track.objects.all().order_by('-createdate')[offset:offset+limit]

def get_current_playing_track():
    stdout_buffer = TemporaryFile()
    stderr_buffer = TemporaryFile()

    p = Popen("/usr/bin/mpc --format '%file%'",bufsize=1,
              stdout=stdout_buffer,stderr=stderr_buffer,
              close_fds=True,shell=True)
    ret = p.wait()
    stdout_buffer.seek(0)
    stderr_buffer.seek(0)
    stdout = stdout_buffer.read()
    stderr = stderr_buffer.read()
    stdout_buffer.close()
    stderr_buffer.close()
    filename = stdout.split("\n")[0].strip()
    full_filename = os.path.join("./home/anders/MyMusic",filename)

    try:
        return Track.objects.get(url=full_filename)
    except Track.DoesNotExist:
        return None

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
