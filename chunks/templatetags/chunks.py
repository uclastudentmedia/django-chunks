from django import template
from django.db import models
from django.core.cache import cache

register = template.Library()

Chunk = models.get_model('chunks', 'chunk')
CACHE_PREFIX = "chunk_"

def do_get_chunk(parser, token):
    # split_contents() knows not to split quoted strings.
    tokens = token.split_contents()
    
    cache_time = 0
    varname = None
    if len(tokens) == 2:
        tag_name, key = tokens
    elif len(tokens) == 3:
        tag_name, key, cache_time = tokens
    elif len(tokens) == 4:
        tag_name, key, separator, varname = tokens
        if separator != 'as':
            raise template.TemplateSyntaxError, "The second to last argument should be the word as."
    elif len(tokens) == 5:
        tag_name, key, cache_time, separator, varname = tokens
        if separator != 'as':
            raise template.TemplateSyntaxError, "The second to last argument should be the word as."
    else:
        raise template.TemplateSyntaxError, "%r tag should have 2 to 5 arguments" % (tokens[0],)
    
    # Check to see if the key is properly double/single quoted
    if not (key[0] == key[-1] and key[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    # Send key without quotes and caching time
    return ChunkNode(key[1:-1], cache_time, varname)

class ChunkNode(template.Node):
    def __init__(self, key, cache_time=0, varname=None):
       self.key = key
       self.cache_time = cache_time
       self.varname = varname
    
    def render(self, context):
        try:
            cache_key = CACHE_PREFIX + self.key
            c = cache.get(cache_key)
            if c is None:
                c = Chunk.objects.get(key=self.key)
                cache.set(cache_key, c, int(self.cache_time))
            chunk = c
        except Chunk.DoesNotExist:
            chunk = None
        if self.varname:
            context[self.varname] = chunk
            return ''
        else:
            return chunk.content

register.tag('chunk', do_get_chunk)
