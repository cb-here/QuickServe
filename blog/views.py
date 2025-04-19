from django.shortcuts import render, get_object_or_404
from .models import Blog

def blogs(request):
    order_by = request.GET.get('order_by', '-created_at')
    blogs = Blog.objects.all().order_by(order_by)
    context = {
        'blogs': blogs,
        'title': 'Blogs'
    }
    return render(request, 'blog/blogs.html', context)

def blog_detail(request, blog_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)
    context = {
        'blog': blog,
        'title': blog.title
    }
    return render(request, 'blog/blog_detail.html', context)