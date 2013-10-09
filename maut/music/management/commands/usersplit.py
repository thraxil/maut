from music.models import Track, UserRating, UserPlaycount
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, **options):
        u = User.objects.get(username='anp8')
        i = 0
        for t in Track.objects.all():
            rating = t.rating or 0
            playcounter = t.playcounter or 0
            accessdate = t.accessdate or 0
            UserRating.objects.create(user=u, track=t, rating=rating)
            UserPlaycount.objects.create(user=u, track=t,
                                         playcounter=playcounter,
                                         accessdate=accessdate)
            i = i + 1
            if (i % 100) == 0:
                print str(i)
