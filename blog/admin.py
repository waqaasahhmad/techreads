# blog/admin.py
# (No changes strictly needed here for CKEditor to work on the 'body' field,
# as it's picked up from the model field type.
# Your existing PostAdmin should be fine.)

from django.contrib import admin
from .models import Post
from django.utils.html import format_html

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status', 'display_title_image')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
    # If you have 'fields' or 'fieldsets' defined, ensure 'body' is included.
    # fields = ('title', 'slug', 'author', 'body', 'title_image', 'status', 'publish')

    def display_title_image(self, obj):
        if obj.title_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.title_image.url)
        return "No Image"
    display_title_image.short_description = 'Image'


