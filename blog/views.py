
# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Post

def landing_page(request):
    """
    View for the landing page.
    Displays a few recent published posts.
    """
    recent_posts = Post.objects.filter(status='published').order_by('-publish')[:3] # Get 3 most recent
    return render(request,
                  'blog/landing_page.html',
                  {'recent_posts': recent_posts})

def post_list(request):
    """
    View to display a list of all published posts.
    """
    posts = Post.objects.filter(status='published')
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts})

def post_detail(request, year, month, day, post_slug): # Renamed 'post' to 'post_slug' for clarity
    """
    View to display a single post.
    """
    post = get_object_or_404(Post,
                             slug=post_slug,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request,
                  'blog/post/detail.html',
                  {'post': post})

def about_page(request):
    """
    View for the About page.
    """
    return render(request, 'blog/about.html')

def contact_page(request):
    """
    View for the Contact page.
    """
    return render(request, 'blog/contact.html')