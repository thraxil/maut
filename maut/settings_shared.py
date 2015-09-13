# Django settings for maut project.
import os.path
from thraxilsettings.shared import common

app = 'maut'
base = os.path.dirname(__file__)

locals().update(common(app=app, base=base))

INSTALLED_APPS += [  # noqa
    'tagging',
    'maut.music',
]
