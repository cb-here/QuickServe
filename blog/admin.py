from django.contrib import admin
from .models import Blog

class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'author', 'slug')
    list_filter = ('title', 'created_at', 'updated_at', 'author')
    
admin.site.register(Blog, BlogAdmin)