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
                       (r'^admin/(.*)', admin.site.root),
		       (r'^survey/',include('survey.urls')),
                       (r'^tinymce/', include('tinymce.urls')),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),

                       (r'^$','music.views.index'),
                       (r'^search/$','music.views.search'),
                       (r'^artist/(?P<id>\d+)/$','music.views.artist'),
                       (r'^artist/(?P<id>\d+)/tag/$','music.views.update_artist_tags'),
                       (r'^album/(?P<id>\d+)/$','music.views.album'),
                       (r'^album/(?P<id>\d+)/playlist/$','music.views.album_playlist'),
                       (r'^album/(?P<id>\d+)/m3u/$','music.views.album_m3u'),
                       (r'^track/(?P<id>\d+)/$','music.views.track'),
                       (r'^track/(?P<id>\d+)/played/$','music.views.played_track'),
                       (r'^track/(?P<id>\d+)/rate/$','music.views.rate_track'),
                       (r'^track/(?P<id>\d+)/tag/$','music.views.update_track_tags'),
                       (r'^track/(?P<id>\d+)/tagup/(?P<tag>.+)/$','music.views.track_tagup'),
                       (r'^track/(?P<id>\d+)/playlist/$','music.views.track_playlist'),
                       (r'^update/$','music.views.update'),
                       (r'^updatedb/$','music.views.updatedb'),
                       (r'^updatedir/$','music.views.updatedir'),
                       (r'^add_from_tahoe/$','music.views.add_from_tahoe'),
                       (r'^deep_updatedb/$','music.views.deep_updatedb'),
                       (r'^queueunrated/$','music.views.queueunrated'),
                       (r'^queuerandom/$','music.views.queuerandom'),
                       (r'^loadipod/$','music.views.load_ipod'),
                       (r'^rate_current/(?P<rating>\d+)/$','music.views.rate_current'),
                       (r'^rating/(?P<rating>\d+)/$','music.views.rating'),
                       (r'^rating/(?P<rating>\d+)/m3u/$','music.views.rating_m3u'),
                       (r'^rating/(?P<rating>\d+)/playm3u/$','music.views.rating_m3u'),
                       (r'^rating/$','music.views.ratings'),
                       (r'^genre/(?P<genre>\d+)/$','music.views.genre'),
                       (r'^genre/$','music.views.genres'),
                       (r'^genre/(?P<genre>\d+)/change/$','music.views.merge_genre'),

                       (r'^tag/$','music.views.tags'),
                       (r'^tag/(?P<tag>.+)/$','music.views.tag'),

                       (r'^yeartop/$','music.views.yeartop'),
                       (r'^facet/$','music.views.facet'),
)
