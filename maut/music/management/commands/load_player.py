from maut.music.models import Track, User
from django.core.management.base import BaseCommand
import random
import requests
import re
import os


username = 'anders'
TARGET = "/mnt/sd/"
LIMIT = 1000


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
        u = User.objects.get(username=username)
        tracks = Track.objects.filter(
            userrating__user=u,
            userrating__rating=10).order_by(
                'artist__name', 'album__name', 'track', 'createdate')
        count = tracks.count()
        idxes = range(count)
        random.shuffle(idxes)
        playlist = open(os.path.join(TARGET, "all.m3u"), "a")
        c = 1
        for i in idxes[:LIMIT]:
            t = tracks[i]
            d = track_dir(t)
            f = track_filename(t)
            url = t.local_download()
            fullpath = os.path.join(TARGET, d, f)
            try:
                os.makedirs(os.path.join(TARGET, d))
            except Exception:
                pass
            print "%03d %s" % (c, fullpath)
            fh = open(fullpath, "w")
            r = requests.get(url)
            fh.write(r.content)
            fh.close()
            playlist.write("%s/%s\n" % (d, f))
            c += 1
        playlist.close()
