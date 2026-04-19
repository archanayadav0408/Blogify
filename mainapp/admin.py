from django.contrib import admin

from .models import Blog, Comment


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "views", "published_at", "updated_at")
    list_filter = ("published_at", "updated_at")
    search_fields = ("title", "subtitle", "author", "content")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("blog", "name", "created_at")
    list_filter = ("created_at",)
    search_fields = ("blog__title", "name", "comment")
