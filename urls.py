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
                       (r'^artist/(?P<id>\d+)/$','music.views.artist'),
                       (r'^album/(?P<id>\d+)/$','music.views.album'),
                       (r'^track/(?P<id>\d+)/$','music.views.track'),
                       (r'^track/(?P<id>\d+)/rate/$','music.views.rate_track'),
                       (r'^update/$','music.views.update'),
                       (r'^updatedb/$','music.views.updatedb'),
                       (r'^queueunrated/$','music.views.queueunrated'),
                       (r'^rate_current/(?P<rating>\d+)/$','music.views.rate_current'),
)
