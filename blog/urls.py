from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.landing_page, name='landing_page'), # Root URL of the app
    path('posts/', views.post_list, name='post_list'),  # All blog posts
    path('posts/<int:year>/<int:month>/<int:day>/<slug:post_slug>/', # Changed 'post' to 'post_slug'
         views.post_detail,
         name='post_detail'),
    path('about/', views.about_page, name='about_page'),
    path('contact/', views.contact_page, name='contact_page'),
]
