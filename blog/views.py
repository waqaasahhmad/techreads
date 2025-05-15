
# blog/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # For Pagination
from .models import Post, Category
from taggit.models import Tag # Import Tag model from taggit
from django.db.models import Q # For Search

def landing_page(request):
    recent_posts = Post.objects.filter(status='published').order_by('-publish')[:3]
    categories = Category.objects.all() # Get all categories for display
    return render(request,
                  'blog/landing_page.html',
                  {'recent_posts': recent_posts, 'categories': categories})

def post_list_view(request, category_slug=None, tag_slug=None):
    object_list = Post.objects.filter(status='published')
    category = None
    tag = None
    page_title = "All Blog Posts"

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        object_list = object_list.filter(category=category)
        page_title = f"Posts in Category: {category.name}"

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag]) # Filter by posts containing the tag
        page_title = f"Posts Tagged: {tag.name}"

    paginator = Paginator(object_list, 5) # 5 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    all_tags = Tag.objects.all()

    return render(request,
                  'blog/post/list.html',
                  {'posts': posts,
                   'page': page, # For pagination template
                   'category': category, # Current category, if any
                   'tag': tag,           # Current tag, if any
                   'page_title': page_title,
                   'categories': categories, # For sidebar/dropdown
                   'all_tags': all_tags}) # For sidebar/dropdown

def post_detail(request, year, month, day, post_slug):
    post = get_object_or_404(Post,
                             slug=post_slug,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    
    # Related Posts Logic (based on shared tags)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(status='published', tags__in=post_tags_ids)\
                                .exclude(id=post.id)
    # Use set to count common tags and order by it, then by publish date
    # This is a more complex way, for simplicity we can just get distinct posts
    # similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    # Simpler:
    similar_posts = list(set(similar_posts))[:4] # Get unique similar posts, limit to 4

    categories = Category.objects.all()
    all_tags = Tag.objects.all()

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'similar_posts': similar_posts,
                   'categories': categories,
                   'all_tags': all_tags})

def about_page(request):
    categories = Category.objects.all()
    all_tags = Tag.objects.all()
    return render(request, 'blog/about.html', {'categories': categories, 'all_tags': all_tags})

def contact_page(request):
    categories = Category.objects.all()
    all_tags = Tag.objects.all()
    return render(request, 'blog/contact.html', {'categories': categories, 'all_tags': all_tags})

# Search View
def search_view(request):
    query = request.GET.get('q')
    results = []
    page_title = "Search Results"

    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) | Q(body__icontains=query) | Q(tags__name__icontains=query), # Search in title, body, or tags
            status='published'
        ).distinct().order_by('-publish')
        page_title = f"Search Results for: \"{query}\""

    paginator = Paginator(results, 5) # 5 posts per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    all_tags = Tag.objects.all()

    return render(request, 'blog/post/list.html', { # Re-use list.html for search results
        'posts': posts,
        'page': page,
        'query': query,
        'page_title': page_title,
        'is_search_results': True, # Flag to slightly alter list.html if needed
        'categories': categories,
        'all_tags': all_tags
    })


# Archive Views (Example for Monthly Archive)
from django.views.generic.dates import MonthArchiveView

class PostMonthArchiveView(MonthArchiveView):
    queryset = Post.objects.filter(status='published')
    date_field = "publish"
    allow_future = False
    template_name = 'blog/post/archive_month.html' # Create this template
    month_format = '%m' # Use numeric month in URL
    context_object_name = 'posts' # To iterate as 'posts' in template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['all_tags'] = Tag.objects.all()
        # context['month'] is already provided by MonthArchiveView
        return context

