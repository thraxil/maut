from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
import os.path
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns('',
                       # Example:
                       # (r'^maut/', include('maut.foo.urls')),
                       ('^accounts/',include('djangowind.urls')),
                       ('^munin/',include('munin.urls')),
                       (r'^admin/', include(admin.site.urls)),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),

                       (r'^$','music.views.index'),
                       (r'^search/$','music.views.search'),
                       (r'^artist/(?P<id>\d+)/$','music.views.artist'),
                       (r'^artist/(?P<id>\d+)/tag/$','music.views.update_artist_tags'),
                       (r'^album/(?P<id>\d+)/$','music.views.album'),
                       (r'^album/(?P<id>\d+)/playlist/$','music.views.album_playlist'),
                       (r'^album/(?P<id>\d+)/m3u/$','music.views.album_m3u'),
                       (r'^album/(?P<id>\d+)/playm3u/$','music.views.album_play_m3u'),
                       (r'^album/(?P<id>\d+)/add_to_playlist/$','music.views.add_album_to_playlist'),
                       (r'^track/(?P<id>\d+)/$','music.views.track'),
                       (r'^track/(?P<id>\d+)/played/$','music.views.played_track'),
                       (r'^track/(?P<id>\d+)/rate/$','music.views.rate_track'),
                       (r'^track/(?P<id>\d+)/tag/$','music.views.update_track_tags'),
                       (r'^track/(?P<id>\d+)/tagup/(?P<tag>.+)/$','music.views.track_tagup'),
                       (r'^track/(?P<id>\d+)/playlist/$','music.views.track_playlist'),
                       (r'^track/(?P<id>\d+)/add_to_playlist/$','music.views.add_track_to_playlist'),
                       (r'^add_from_tahoe/$','music.views.add_from_tahoe'),
                       (r'^randomplaylist/$','music.views.random_playlist'),
                       (r'^rating/(?P<rating>\d+)/$','music.views.rating'),
                       (r'^rating/(?P<rating>\d+)/csv/$','music.views.rating_csv'),
                       (r'^rating/(?P<rating>\d+)/m3u/$','music.views.rating_m3u'),
                       (r'^rating/(?P<rating>\d+)/playm3u/$','music.views.rating_play_m3u'),
                       (r'^rating/$','music.views.ratings'),
                       (r'^genre/(?P<genre>\d+)/$','music.views.genre'),
                       (r'^genre/$','music.views.genres'),
                       (r'^genre/(?P<genre>\d+)/change/$','music.views.merge_genre'),

                       (r'^tag/$','music.views.tags'),
                       (r'^tag/(?P<tag>.+)/$','music.views.tag'),

                       (r'^year/$','music.views.years'),
                       (r'^year/(?P<year>\d+)/$','music.views.year'),
                       (r'^year/(?P<year>\d+)/change/$','music.views.merge_year'),

                       (r'^playlist/$','music.views.playlist_index'),
                       (r'^playlist/create/$','music.views.create_playlist'),
                       (r'^playlist/(?P<id>\d+)/$','music.views.playlist'),
                       (r'^playlist/(?P<id>\d+)/playlist/$',
                        'music.views.playlist_playlist'),
                       (r'^remove_track_from_playlist/(?P<id>\d+)/',
                        'music.views.remove_track_from_playlist'),

                       (r'^yeartop/$','music.views.yeartop'),
                       (r'^facet/$','music.views.facet'),

                       (r'stats/track_count/$','music.views.track_count'),
                       (r'stats/hourly_plays/(?P<username>\w+)/$','music.views.hourly_plays'),
                       (r'stats/unrated_count/(?P<username>\w+)/$','music.views.unrated_count'),
                       (r'stats/total_plays/(?P<username>\w+)/$','music.views.total_plays'),
)
