from models import *

class ArtistAdmin(admin.ModelAdmin): pass
admin.site.register(Artist,ArtistAdmin)

class GenreAdmin(admin.ModelAdmin): pass
admin.site.register(Genre,GenreAdmin)

class TrackAdmin(admin.ModelAdmin): pass
admin.site.register(Track,TrackAdmin)

class LabelAdmin(admin.ModelAdmin): pass
admin.site.register(Label,LabelAdmin)

