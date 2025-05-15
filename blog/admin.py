# blog/admin.py

from django.contrib import admin
from .models import Post, Category # Import Category
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'category', 'publish', 'status', 'display_tags', 'display_title_image') # Added category, display_tags
    list_filter = ('status', 'created', 'publish', 'author', 'category', 'tags') # Added category, tags
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
    # Ensure category and tags are in fields if you customize the form layout
    fields = ('title', 'slug', 'author', 'category', 'tags', 'body', 'title_image', 'status', 'publish')

    def display_title_image(self, obj):
        if obj.title_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.title_image.url)
        return "No Image"
    display_title_image.short_description = 'Image'

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'Tags'
