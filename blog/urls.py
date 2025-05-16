from django.urls import path
from . import views
from .views import PostMonthArchiveView # Assuming this is your archive view
from django.contrib.auth import views as auth_views # For built-in auth views

app_name = 'blog'

urlpatterns = [
    # Core Blog URLs
    path('', views.landing_page, name='landing_page'),
    path('posts/', views.post_list_view, name='post_list'),
    path('category/<slug:category_slug>/', views.post_list_view, name='post_list_by_category'),
    path('tag/<slug:tag_slug>/', views.post_list_view, name='post_list_by_tag'),
    path('posts/<int:year>/<int:month>/<int:day>/<slug:post_slug>/',
         views.post_detail,
         name='post_detail'),
    path('about/', views.about_page, name='about_page'),
    path('contact/', views.contact_page, name='contact_page'), # Functional contact form view
    path('search/', views.search_view, name='search_view'),
    path('archive/<int:year>/<int:month>/', PostMonthArchiveView.as_view(), name="post_month_archive"),

    # Newsletter Subscription URL
    path('newsletter/subscribe/', views.newsletter_subscribe_view, name='newsletter_subscribe'),

    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'), # Specify template if not default
    path('logout/', views.logout_view, name='logout'), # Custom logout view

    # Placeholder for future password reset URLs (requires more templates)
    # path('password_reset/',
    #      auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'),
    #      name='password_reset'),
    # path('password_reset/done/',
    #      auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
    #      name='password_reset_done'),
    # path('reset/<uidb64>/<token>/',
    #      auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
    #      name='password_reset_confirm'),
    # path('reset/done/',
    #      auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
    #      name='password_reset_complete'),
]
