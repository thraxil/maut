# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'RelatedArtists'
        db.delete_table(u'related_artists')


    def backwards(self, orm):
        # Adding model 'RelatedArtists'
        db.create_table(u'related_artists', (
            ('suggestion', self.gf('django.db.models.fields.TextField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('changedate', self.gf('django.db.models.fields.IntegerField')()),
            ('artist', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'music', ['RelatedArtists'])


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'music.album': {
            'Meta': {'object_name': 'Album', 'db_table': "u'album'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        u'music.artist': {
            'Meta': {'object_name': 'Artist', 'db_table': "u'artist'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'music.composer': {
            'Meta': {'object_name': 'Composer', 'db_table': "u'composer'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        u'music.genre': {
            'Meta': {'object_name': 'Genre', 'db_table': "u'genre'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'music.images': {
            'Meta': {'object_name': 'Images', 'db_table': "u'images'"},
            'album': ('django.db.models.fields.TextField', [], {}),
            'artist': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.TextField', [], {})
        },
        u'music.lyrics': {
            'Meta': {'object_name': 'Lyrics', 'db_table': "u'lyrics'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lyrics': ('django.db.models.fields.TextField', [], {}),
            'url': ('django.db.models.fields.TextField', [], {})
        },
        u'music.playlist': {
            'Meta': {'object_name': 'Playlist'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'music.playlisttrack': {
            'Meta': {'ordering': "(u'_order',)", 'object_name': 'PlaylistTrack'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'playlist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['music.Playlist']"}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['music.Track']"})
        },
        u'music.setting': {
            'Meta': {'object_name': 'Setting'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'music.track': {
            'Meta': {'ordering': "('album__name', 'discnumber', 'track', 'title')", 'object_name': 'Track', 'db_table': "u'tags'"},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['music.Album']", 'db_column': "'album'"}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['music.Artist']", 'db_column': "'artist'"}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {}),
            'bpm': ('django.db.models.fields.FloatField', [], {}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'composer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['music.Composer']", 'db_column': "'composer'"}),
            'createdate': ('django.db.models.fields.IntegerField', [], {}),
            'discnumber': ('django.db.models.fields.IntegerField', [], {}),
            'filesize': ('django.db.models.fields.IntegerField', [], {}),
            'filetype': ('django.db.models.fields.IntegerField', [], {}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['music.Genre']", 'db_column': "'genre'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {}),
            'modifydate': ('django.db.models.fields.IntegerField', [], {}),
            'sampler': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'samplerate': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'track': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '0'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['music.Year']", 'db_column': "'year'"})
        },
        u'music.userplaycount': {
            'Meta': {'object_name': 'UserPlaycount'},
            'accessdate': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playcounter': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['music.Track']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'music.userrating': {
            'Meta': {'object_name': 'UserRating'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['music.Track']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'music.year': {
            'Meta': {'object_name': 'Year', 'db_table': "u'year'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['music']
