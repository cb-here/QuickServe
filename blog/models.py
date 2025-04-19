from django.db import models
from autoslug import AutoSlugField 
from tinymce.models import HTMLField

class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = HTMLField()
    author = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    slug = AutoSlugField(populate_from='title', unique=True, null=True)
    def __str__(self):
        return self.title