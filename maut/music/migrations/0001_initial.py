# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'album',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
            ],
            options={
                'db_table': 'artist',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Composer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'composer',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
            ],
            options={
                'db_table': 'genre',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.TextField()),
                ('artist', models.TextField()),
                ('album', models.TextField()),
            ],
            options={
                'db_table': 'images',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Lyrics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.TextField()),
                ('lyrics', models.TextField()),
            ],
            options={
                'db_table': 'lyrics',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('description', models.TextField(default=b'', null=True, blank=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlaylistTrack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.TextField(default=b'', null=True, blank=True)),
                ('playlist', models.ForeignKey(to='music.Playlist')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('value', models.CharField(max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=256)),
                ('createdate', models.IntegerField()),
                ('modifydate', models.IntegerField()),
                ('title', models.CharField(max_length=256)),
                ('comment', models.TextField()),
                ('track', models.DecimalField(max_digits=4, decimal_places=0)),
                ('discnumber', models.IntegerField()),
                ('bitrate', models.IntegerField()),
                ('length', models.IntegerField()),
                ('samplerate', models.IntegerField()),
                ('filesize', models.IntegerField()),
                ('filetype', models.IntegerField()),
                ('sampler', models.BooleanField(default=False)),
                ('bpm', models.FloatField()),
                ('album', models.ForeignKey(to='music.Album', db_column=b'album')),
                ('artist', models.ForeignKey(to='music.Artist', db_column=b'artist')),
                ('composer', models.ForeignKey(to='music.Composer', db_column=b'composer')),
                ('genre', models.ForeignKey(to='music.Genre', db_column=b'genre')),
            ],
            options={
                'ordering': ('album__name', 'discnumber', 'track', 'title'),
                'db_table': 'tags',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserPlaycount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('playcounter', models.IntegerField(default=0)),
                ('accessdate', models.IntegerField()),
                ('track', models.ForeignKey(to='music.Track')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating', models.IntegerField(default=0)),
                ('track', models.ForeignKey(to='music.Track')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Year',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'year',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='track',
            name='year',
            field=models.ForeignKey(to='music.Year', db_column=b'year'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='playlisttrack',
            name='track',
            field=models.ForeignKey(to='music.Track'),
            preserve_default=True,
        ),
        migrations.AlterOrderWithRespectTo(
            name='playlisttrack',
            order_with_respect_to='playlist',
        ),
    ]
