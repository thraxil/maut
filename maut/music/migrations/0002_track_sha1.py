# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='sha1',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
    ]
