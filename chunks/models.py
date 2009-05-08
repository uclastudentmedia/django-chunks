from django.db import models
from populous_inlines.fields import InlineField

class Chunk(models.Model):
    """
    A Chunk is a piece of content associated
    with a unique key that can be inserted into
    any template with the use of a special template
    tag
    """
    key = models.CharField(help_text="A unique name for this chunk of content", blank=False, max_length=255, unique=True)
    content = InlineField(blank=True)

    def __unicode__(self):
        return u"%s" % (self.key,)
