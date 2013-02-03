# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Genre'
        db.create_table(u'genre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('music', ['Genre'])

        # Adding model 'Year'
        db.create_table(u'year', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('music', ['Year'])

        # Adding model 'Images'
        db.create_table(u'images', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.TextField')()),
            ('artist', self.gf('django.db.models.fields.TextField')()),
            ('album', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('music', ['Images'])

        # Adding model 'Lyrics'
        db.create_table(u'lyrics', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.TextField')()),
            ('lyrics', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('music', ['Lyrics'])

        # Adding model 'Album'
        db.create_table(u'album', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('music', ['Album'])

        # Adding model 'Artist'
        db.create_table(u'artist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('music', ['Artist'])

        # Adding model 'Composer'
        db.create_table(u'composer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('music', ['Composer'])

        # Adding model 'Setting'
        db.create_table('music_setting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('music', ['Setting'])

        # Adding model 'Track'
        db.create_table(u'tags', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('createdate', self.gf('django.db.models.fields.IntegerField')()),
            ('modifydate', self.gf('django.db.models.fields.IntegerField')()),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Album'], db_column='album')),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Artist'], db_column='artist')),
            ('composer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Composer'], db_column='composer')),
            ('genre', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Genre'], db_column='genre')),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Year'], db_column='year')),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('track', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=0)),
            ('discnumber', self.gf('django.db.models.fields.IntegerField')()),
            ('bitrate', self.gf('django.db.models.fields.IntegerField')()),
            ('length', self.gf('django.db.models.fields.IntegerField')()),
            ('samplerate', self.gf('django.db.models.fields.IntegerField')()),
            ('filesize', self.gf('django.db.models.fields.IntegerField')()),
            ('filetype', self.gf('django.db.models.fields.IntegerField')()),
            ('sampler', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('bpm', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('music', ['Track'])

        # Adding model 'UserRating'
        db.create_table('music_userrating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Track'])),
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('music', ['UserRating'])

        # Adding model 'UserPlaycount'
        db.create_table('music_userplaycount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Track'])),
            ('playcounter', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('accessdate', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('music', ['UserPlaycount'])

        # Adding model 'Playlist'
        db.create_table('music_playlist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('description', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
        ))
        db.send_create_signal('music', ['Playlist'])

        # Adding model 'PlaylistTrack'
        db.create_table('music_playlisttrack', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('playlist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Playlist'])),
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['music.Track'])),
            ('note', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('music', ['PlaylistTrack'])

        # Adding model 'RelatedArtists'
        db.create_table(u'related_artists', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('artist', self.gf('django.db.models.fields.TextField')()),
            ('suggestion', self.gf('django.db.models.fields.TextField')()),
            ('changedate', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('music', ['RelatedArtists'])

        # Adding model 'Amazon'
        db.create_table(u'amazon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asin', self.gf('django.db.models.fields.TextField')()),
            ('locale', self.gf('django.db.models.fields.TextField')()),
            ('filename', self.gf('django.db.models.fields.TextField')()),
            ('refetchdate', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('music', ['Amazon'])


    def backwards(self, orm):
        # Deleting model 'Genre'
        db.delete_table(u'genre')

        # Deleting model 'Year'
        db.delete_table(u'year')

        # Deleting model 'Images'
        db.delete_table(u'images')

        # Deleting model 'Lyrics'
        db.delete_table(u'lyrics')

        # Deleting model 'Album'
        db.delete_table(u'album')

        # Deleting model 'Artist'
        db.delete_table(u'artist')

        # Deleting model 'Composer'
        db.delete_table(u'composer')

        # Deleting model 'Setting'
        db.delete_table('music_setting')

        # Deleting model 'Track'
        db.delete_table(u'tags')

        # Deleting model 'UserRating'
        db.delete_table('music_userrating')

        # Deleting model 'UserPlaycount'
        db.delete_table('music_userplaycount')

        # Deleting model 'Playlist'
        db.delete_table('music_playlist')

        # Deleting model 'PlaylistTrack'
        db.delete_table('music_playlisttrack')

        # Deleting model 'RelatedArtists'
        db.delete_table(u'related_artists')

        # Deleting model 'Amazon'
        db.delete_table(u'amazon')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'music.album': {
            'Meta': {'object_name': 'Album', 'db_table': "u'album'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'music.amazon': {
            'Meta': {'object_name': 'Amazon', 'db_table': "u'amazon'"},
            'asin': ('django.db.models.fields.TextField', [], {}),
            'filename': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locale': ('django.db.models.fields.TextField', [], {}),
            'refetchdate': ('django.db.models.fields.IntegerField', [], {})
        },
        'music.artist': {
            'Meta': {'object_name': 'Artist', 'db_table': "u'artist'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'music.composer': {
            'Meta': {'object_name': 'Composer', 'db_table': "u'composer'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'music.genre': {
            'Meta': {'object_name': 'Genre', 'db_table': "u'genre'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'music.images': {
            'Meta': {'object_name': 'Images', 'db_table': "u'images'"},
            'album': ('django.db.models.fields.TextField', [], {}),
            'artist': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.TextField', [], {})
        },
        'music.lyrics': {
            'Meta': {'object_name': 'Lyrics', 'db_table': "u'lyrics'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lyrics': ('django.db.models.fields.TextField', [], {}),
            'url': ('django.db.models.fields.TextField', [], {})
        },
        'music.playlist': {
            'Meta': {'object_name': 'Playlist'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'music.playlisttrack': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'PlaylistTrack'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'playlist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Playlist']"}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Track']"})
        },
        'music.relatedartists': {
            'Meta': {'object_name': 'RelatedArtists', 'db_table': "u'related_artists'"},
            'artist': ('django.db.models.fields.TextField', [], {}),
            'changedate': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'suggestion': ('django.db.models.fields.TextField', [], {})
        },
        'music.setting': {
            'Meta': {'object_name': 'Setting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'music.track': {
            'Meta': {'ordering': "('album__name', 'discnumber', 'track', 'title')", 'object_name': 'Track', 'db_table': "u'tags'"},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Album']", 'db_column': "'album'"}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Artist']", 'db_column': "'artist'"}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {}),
            'bpm': ('django.db.models.fields.FloatField', [], {}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'composer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Composer']", 'db_column': "'composer'"}),
            'createdate': ('django.db.models.fields.IntegerField', [], {}),
            'discnumber': ('django.db.models.fields.IntegerField', [], {}),
            'filesize': ('django.db.models.fields.IntegerField', [], {}),
            'filetype': ('django.db.models.fields.IntegerField', [], {}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Genre']", 'db_column': "'genre'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {}),
            'modifydate': ('django.db.models.fields.IntegerField', [], {}),
            'sampler': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'samplerate': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'track': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '0'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Year']", 'db_column': "'year'"})
        },
        'music.userplaycount': {
            'Meta': {'object_name': 'UserPlaycount'},
            'accessdate': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playcounter': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Track']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'music.userrating': {
            'Meta': {'object_name': 'UserRating'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['music.Track']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'music.year': {
            'Meta': {'object_name': 'Year', 'db_table': "u'year'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['music']
