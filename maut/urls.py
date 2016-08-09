from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
import django.contrib.auth.urls
import maut.music.views as views
admin.autodiscover()

urlpatterns = [
    url(r'^accounts/', include(django.contrib.auth.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^uploads/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

    url(r'^$', views.IndexView.as_view()),
    url(r'smoketest/', include('smoketest.urls')),
    url(r'^search/$', views.SearchView.as_view()),
    url(r'^artist/(?P<pk>\d+)/$', views.ArtistView.as_view()),
    url(r'^artist/(?P<id>\d+)/tag/$', 'maut.music.views.update_artist_tags'),
    url(r'^album/(?P<id>\d+)/$', 'maut.music.views.album'),
    url(r'^album/(?P<id>\d+)/playlist/$', 'maut.music.views.album_playlist'),
    url(r'^album/(?P<id>\d+)/m3u/$', 'maut.music.views.album_m3u'),
    url(r'^album/(?P<id>\d+)/playm3u/$', 'maut.music.views.album_play_m3u'),
    url(r'^album/(?P<id>\d+)/add_to_playlist/$',
        'maut.music.views.add_album_to_playlist'),
    url(r'^track/(?P<id>\d+)/$', 'maut.music.views.track'),
    url(r'^track/(?P<id>\d+)/played/$', 'maut.music.views.played_track'),
    url(r'^track/(?P<id>\d+)/rate/$', 'maut.music.views.rate_track'),
    url(r'^track/(?P<id>\d+)/tag/$', 'maut.music.views.update_track_tags'),
    url(r'^track/(?P<id>\d+)/tagup/(?P<tag>.+)/$',
        'maut.music.views.track_tagup'),
    url(r'^track/(?P<id>\d+)/playlist/$', 'maut.music.views.track_playlist'),
    url(r'^track/(?P<id>\d+)/add_to_playlist/$',
        'maut.music.views.add_track_to_playlist'),
    url(r'^randomplaylist/$', 'maut.music.views.random_playlist'),
    url(r'^rating/(?P<rating>\d+)/$', 'maut.music.views.rating'),
    url(r'^rating/(?P<rating>\d+)/csv/$', 'maut.music.views.rating_csv'),
    url(r'^rating/(?P<rating>\d+)/m3u/$', 'maut.music.views.rating_m3u'),
    url(r'^rating/(?P<rating>\d+)/playm3u/$',
        'maut.music.views.rating_play_m3u'),
    url(r'^rating/$', 'maut.music.views.ratings'),
    url(r'^genre/(?P<genre>\d+)/$', 'maut.music.views.genre'),
    url(r'^genre/$', 'maut.music.views.genres'),
    url(r'^genre/(?P<genre>\d+)/change/$', 'maut.music.views.merge_genre'),

    url(r'^tag/$', 'maut.music.views.tags'),
    url(r'^tag/(?P<tag>.+)/$', 'maut.music.views.tag'),

    url(r'^year/$', 'maut.music.views.years'),
    url(r'^year/(?P<year>\d+)/$', 'maut.music.views.year'),
    url(r'^year/(?P<year>\d+)/change/$', 'maut.music.views.merge_year'),

    url(r'^playlist/$', views.PlaylistIndexView.as_view()),
    url(r'^playlist/create/$', 'maut.music.views.create_playlist'),
    url(r'^playlist/(?P<id>\d+)/$', 'maut.music.views.playlist'),
    url(r'^playlist/(?P<id>\d+)/playlist/$',
        'maut.music.views.playlist_playlist'),
    url(r'^remove_track_from_playlist/(?P<id>\d+)/',
        'maut.music.views.remove_track_from_playlist'),

    url(r'^yeartop/$', 'maut.music.views.yeartop'),
    url(r'^facet/$', 'maut.music.views.facet'),
]
