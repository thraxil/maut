# flake8: noqa
from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/maut/maut/maut/templates",
)

MEDIA_ROOT = '/var/www/maut/uploads/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

STATIC_ROOT = "/var/www/maut/maut/media/"
STATICFILES_DIRS = ()

if 'migrate' not in sys.argv:
    INSTALLED_APPS = INSTALLED_APPS + [
        'raven.contrib.django.raven_compat',
    ]


# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass
