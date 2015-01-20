from maut.music.models import Track, User
from django.conf import settings
from django.core.management.base import BaseCommand
import random
import requests
import re
import os

TAHOE_BASE = settings.TAHOE_BASE
HAKMES_BASE = settings.HAKMES_BASE


def dir_safe(s):
    s = s.lower()
    s = re.sub(r'\W+', '_', s)
    if len(s) < 1:
        s = s + "_"
    return s


def track_dir(t):
    return dir_safe(t.artist.name) + "/" + dir_safe(t.album.name)


def track_filename(t):
    return "%02d_%s_%d.%s" % (t.track, dir_safe(t.title), t.id,
                              t.extension())


class Command(BaseCommand):
    def handle(self, **options):
        tracks = Track.objects.filter(sha1="")
        count = tracks.count()
        for idx, t in enumerate(tracks):
            try:
                print "[%04d/%04d] %s - %s" % (
                    idx, count,
                    t.artist.name, t.title)
                tahoe_url = t.local_download()

                fullpath = "/tmp/download." + t.extension()
                fh = open(fullpath, "w")
                r = requests.get(tahoe_url)
                fh.write(r.content)
                fh.close()

                print "...downloaded..."

                files = {'file': (fullpath, open(fullpath, 'rb'), t.mimetype())}
                r = requests.post(HAKMES_BASE, files=files)
                t.sha1 = r.json()['key']
                t.save()
                print "uploaded to hakmes"
            except Exception, e:
                print "!!!exception!!!"
                print str(e)
                

