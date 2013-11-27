from django.conf.urls.defaults import patterns, include
from django.contrib import admin
from django.conf import settings
import maut.music.views as views
admin.autodiscover()

urlpatterns = patterns(
    '',
    ('^accounts/', include('djangowind.urls')),
    ('^munin/', include('munin.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT}),

    (r'^$', views.IndexView.as_view()),
    (r'^search/$', views.SearchView.as_view()),
    (r'^artist/(?P<pk>\d+)/$', views.ArtistView.as_view()),
    (r'^artist/(?P<id>\d+)/tag/$', 'maut.music.views.update_artist_tags'),
    (r'^album/(?P<id>\d+)/$', 'maut.music.views.album'),
    (r'^album/(?P<id>\d+)/playlist/$', 'maut.music.views.album_playlist'),
    (r'^album/(?P<id>\d+)/m3u/$', 'maut.music.views.album_m3u'),
    (r'^album/(?P<id>\d+)/playm3u/$', 'maut.music.views.album_play_m3u'),
    (r'^album/(?P<id>\d+)/add_to_playlist/$',
     'maut.music.views.add_album_to_playlist'),
    (r'^track/(?P<id>\d+)/$', 'maut.music.views.track'),
    (r'^track/(?P<id>\d+)/played/$', 'maut.music.views.played_track'),
    (r'^track/(?P<id>\d+)/rate/$', 'maut.music.views.rate_track'),
    (r'^track/(?P<id>\d+)/tag/$', 'maut.music.views.update_track_tags'),
    (r'^track/(?P<id>\d+)/tagup/(?P<tag>.+)/$',
     'maut.music.views.track_tagup'),
    (r'^track/(?P<id>\d+)/playlist/$', 'maut.music.views.track_playlist'),
    (r'^track/(?P<id>\d+)/add_to_playlist/$',
     'maut.music.views.add_track_to_playlist'),
    (r'^add_from_tahoe/$', 'maut.music.views.add_from_tahoe'),
    (r'^randomplaylist/$', 'maut.music.views.random_playlist'),
    (r'^rating/(?P<rating>\d+)/$', 'maut.music.views.rating'),
    (r'^rating/(?P<rating>\d+)/csv/$', 'maut.music.views.rating_csv'),
    (r'^rating/(?P<rating>\d+)/m3u/$', 'maut.music.views.rating_m3u'),
    (r'^rating/(?P<rating>\d+)/playm3u/$',
     'maut.music.views.rating_play_m3u'),
    (r'^rating/$', 'maut.music.views.ratings'),
    (r'^genre/(?P<genre>\d+)/$', 'maut.music.views.genre'),
    (r'^genre/$', 'maut.music.views.genres'),
    (r'^genre/(?P<genre>\d+)/change/$', 'maut.music.views.merge_genre'),

    (r'^tag/$', 'maut.music.views.tags'),
    (r'^tag/(?P<tag>.+)/$', 'maut.music.views.tag'),

    (r'^year/$', 'maut.music.views.years'),
    (r'^year/(?P<year>\d+)/$', 'maut.music.views.year'),
    (r'^year/(?P<year>\d+)/change/$', 'maut.music.views.merge_year'),

    (r'^playlist/$', views.PlaylistIndexView.as_view()),
    (r'^playlist/create/$', 'maut.music.views.create_playlist'),
    (r'^playlist/(?P<id>\d+)/$', 'maut.music.views.playlist'),
    (r'^playlist/(?P<id>\d+)/playlist/$',
     'maut.music.views.playlist_playlist'),
    (r'^remove_track_from_playlist/(?P<id>\d+)/',
     'maut.music.views.remove_track_from_playlist'),

    (r'^yeartop/$', 'maut.music.views.yeartop'),
    (r'^facet/$', 'maut.music.views.facet'),

    (r'stats/track_count/$', 'maut.music.views.track_count'),
    (r'stats/hourly_plays/(?P<username>\w+)/$',
     'maut.music.views.hourly_plays'),
    (r'stats/unrated_count/(?P<username>\w+)/$',
     'maut.music.views.unrated_count'),
    (r'stats/total_plays/(?P<username>\w+)/$', 'maut.music.views.total_plays'),
)
