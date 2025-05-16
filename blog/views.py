
# blog/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # For Pagination
from .models import Post, Category
from taggit.models import Tag # Import Tag model from taggit
from django.db.models import Q # For Search
from .forms import CommentForm # Import CommentForm
from django.core.mail import send_mail
from django.conf import settings # To get DEFAULT_FROM_EMAIL or admin email
from .forms import CommentForm, ContactForm # Add ContactForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect # Ensure redirect is imported
from .forms import CommentForm, ContactForm, NewsletterSubscriptionForm # Add NewsletterSubscriptionForm
from .models import Post, Category, Comment, Subscriber # Add Subscriber
from django.http import JsonResponse # For AJAX response if used later


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
                   'all_tags': all_tags,
                    'comment_form': comment_form, 
                   })

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

def post_detail(request, year, month, day, post_slug):
    post = get_object_or_404(Post,
                             slug=post_slug,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    
    comments = post.comments.filter(active=True) # Get active comments for this post
    new_comment = None
    comment_form = CommentForm(user=request.user if request.user.is_authenticated else None) # Pass user to form
    comments = post.comments.filter(active=True)
    comment_form = CommentForm(user=request.user if request.user.is_authenticated else None)    

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST, user=request.user if request.user.is_authenticated else None)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            if request.user.is_authenticated:
                new_comment.user = request.user
                # If name/email were hidden and not submitted, populate from user
                if not new_comment.name: new_comment.name = request.user.get_full_name() or request.user.username
                if not new_comment.email: new_comment.email = request.user.email
            new_comment.save()
            # Optionally, redirect to the same page or show a success message
            # return redirect(post.get_absolute_url() + '#comments') # Redirect to comments section
            comment_form = CommentForm(user=request.user if request.user.is_authenticated else None) # Reset form
        # else:
            # Form is invalid, it will be re-rendered with errors

    # Related Posts Logic
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(status='published', tags__in=post_tags_ids)\
                                .exclude(id=post.id)
    similar_posts = list(set(similar_posts))[:4]

    categories = Category.objects.all()
    all_tags = Tag.objects.all()

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment, # The comment just submitted (or None)
                   'comment_form': comment_form,
                   'similar_posts': similar_posts,
                   'categories': categories,
                   'all_tags': all_tags})

def contact_page(request):
    form_submitted = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message_body = form.cleaned_data['message']

            email_subject = f'New Contact Form Submission: {subject}'
            email_message = f'Name: {name}\nEmail: {from_email}\n\nMessage:\n{message_body}'
            
            try:
                # Send email
                # Make sure ADMINS is set in settings.py for settings.ADMINS[0][1]
                # Or use a hardcoded recipient list for testing
                admin_emails = [admin[1] for admin in settings.ADMINS] if hasattr(settings, 'ADMINS') and settings.ADMINS else ['yourdefaultadmin@example.com']

                send_mail(
                    email_subject,
                    email_message,
                    from_email, # Sender's email (user input)
                    admin_emails, # List of recipients (your admin email(s))
                    fail_silently=False,
                )
                form_submitted = True # To show a success message
                form = ContactForm() # Clear the form
            except Exception as e:
                # Handle email sending error (e.g., log it, show an error message)
                print(f"Error sending contact email: {e}") # Log to console for now
                # You might want to add a message to the user here
                pass # Or add an error message to the form/context
    else:
        form = ContactForm()

    categories = Category.objects.all()
    all_tags = Tag.objects.all()
    return render(request, 'blog/contact.html', {
        'form': form,
        'form_submitted': form_submitted,
        'categories': categories,
        'all_tags': all_tags
    })

# ... (search_view, PostMonthArchiveView) ...
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log the user in directly after registration
            return redirect('blog:landing_page') # Redirect to home or a profile page
    else:
        form = UserCreationForm()
    categories = Category.objects.all() # For sidebar
    all_tags = Tag.objects.all()      # For sidebar
    return render(request, 'registration/register.html', {
        'form': form,
        'categories': categories,
        'all_tags': all_tags
    })

# Django provides built-in views for login and logout,
# but you can create custom ones if needed for more control or different templates.
# For now, we'll use Django's built-in ones and just provide templates.

@login_required # Decorator to ensure user is logged in
def logout_view(request):
    logout(request)
    return redirect('blog:landing_page') # Redirect to home after logout

def newsletter_subscribe_view(request):
    if request.method == 'POST':
        form = NewsletterSubscriptionForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                # For AJAX requests, you might return JsonResponse
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': 'Successfully subscribed!'})
                # For regular form submissions, redirect or show message
                # messages.success(request, 'Successfully subscribed!') # Requires Django messages framework setup
                return redirect(request.META.get('HTTP_REFERER', 'blog:landing_page') + '?subscribed=true') # Redirect back
            except Exception as e: # Handles unique constraint violation if email already exists
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'This email is already subscribed or an error occurred.'}, status=400)
                # messages.error(request, 'This email is already subscribed or an error occurred.')
                return redirect(request.META.get('HTTP_REFERER', 'blog:landing_page') + '?subscribed=false&error=exists')
        else:
            # Form is invalid
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Invalid email address.'}, status=400)
            # messages.error(request, 'Invalid email address.')
            return redirect(request.META.get('HTTP_REFERER', 'blog:landing_page') + '?subscribed=false&error=invalid')

    # If GET request or other, redirect to home or show error
    return redirect('blog:landing_page')
