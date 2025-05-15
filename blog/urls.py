# blog/urls.py

from django.urls import path
from . import views
from .views import PostMonthArchiveView # Import archive view

app_name = 'blog'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('posts/', views.post_list_view, name='post_list'), # Main post list
    path('category/<slug:category_slug>/', views.post_list_view, name='post_list_by_category'), # Posts by category
    path('tag/<slug:tag_slug>/', views.post_list_view, name='post_list_by_tag'), # Posts by tag
    path('posts/<int:year>/<int:month>/<int:day>/<slug:post_slug>/',
         views.post_detail,
         name='post_detail'),
    path('about/', views.about_page, name='about_page'),
    path('contact/', views.contact_page, name='contact_page'),
    path('search/', views.search_view, name='search_view'), # Search results
    path('archive/<int:year>/<int:month>/', PostMonthArchiveView.as_view(), name="post_month_archive"), # Monthly archive
]