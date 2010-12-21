from django import template
from music.models import Track

register = template.Library()

class GetPlaycountNode(template.Node):
    def __init__(self,track,var_name):
        self.track = track
        self.var_name = var_name
    def render(self,context):
        t = context[self.track]
        u = context['request'].user
        playcounter = t.userplaycount(u).playcounter
        context[self.var_name] = playcounter
        return ''

@register.tag('getplaycount')
def getrating(parser,token):
    track = token.split_contents()[1:][0]
    var_name = token.split_contents()[1:][2]
    return GetPlaycountNode(track,var_name)

class GetAccessDateNode(template.Node):
    def __init__(self,track,var_name):
        self.track = track
        self.var_name = var_name
    def render(self,context):
        t = context[self.track]
        u = context['request'].user
        accessdate = t.accessed(u)
        context[self.var_name] = accessdate
        return ''

@register.tag('getaccessdate')
def getaccessdate(parser,token):
    track = token.split_contents()[1:][0]
    var_name = token.split_contents()[1:][2]
    return GetAccessDateNode(track,var_name)
