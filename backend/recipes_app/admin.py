from django.contrib import admin
from .models import Category, Recipe, Comment, Favorite


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "difficulty", "created_at")
    list_filter = ("difficulty", "category")
    search_fields = ("title", "description", "ingredients")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "author", "is_chef_comment", "created_at")
    list_filter = ("is_chef_comment", "created_at")
    search_fields = ("text", "author__username", "recipe__title")
    readonly_fields = ("created_at",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "recipe__title")
    readonly_fields = ("created_at",)
