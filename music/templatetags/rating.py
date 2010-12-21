from django import template
from music.models import Track, UserRating

register = template.Library()

class GetRatingNode(template.Node):
    def __init__(self,track,var_name):
        self.track = track
        self.var_name = var_name
    def render(self,context):
        t = context[self.track]
        u = context['request'].user
        rating = t.userrating(u).rating
        context[self.var_name] = rating
        return ''

@register.tag('getrating')
def getrating(parser,token):
    track = token.split_contents()[1:][0]
    var_name = token.split_contents()[1:][2]
    return GetRatingNode(track,var_name)
