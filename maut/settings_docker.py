# flake8: noqa
from settings_shared import *

from thraxilsettings.docker import common
import os.path

app = 'maut'
base = os.path.dirname(__file__)

locals().update(
    common(
        app=app,
        base=base,
        celery=False,
        INSTALLED_APPS=INSTALLED_APPS,
        STATIC_ROOT=STATIC_ROOT,
    ))

# required settings:
LASTFM_PASSWORD_FILE = os.environ['LASTFM_PASSWORD_FILE']
