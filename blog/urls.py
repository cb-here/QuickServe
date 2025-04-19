from django.urls import path
from . import views

urlpatterns = [
    path("", views.blogs, name='blog'),
    path("blog_detail/<slug:blog_slug>/", views.blog_detail, name='blog_detail')
]