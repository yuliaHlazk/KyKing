from django.urls import path
from recipes_app.views import (
    CategoryListCreate,
    CategoryDetail,
    RecipeListCreate,
    RecipeDetail,
    RecipeVerify,
    CommentListCreate,
    CommentDetail,
    FavoriteListCreate,
    FavoriteDelete,
)

urlpatterns = [
    path("categories/", CategoryListCreate.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryDetail.as_view(), name="category-detail"),
    path("recipes/", RecipeListCreate.as_view(), name="recipe-list-create"),
    path("recipes/<int:pk>/", RecipeDetail.as_view(), name="recipe-detail"),
    path("recipes/<int:pk>/verify/", RecipeVerify.as_view(), name="recipe-verify"),
    path(
        "recipes/<int:recipe_id>/comments/",
        CommentListCreate.as_view(),
        name="comment-list-create",
    ),
    path(
        "comments/<int:pk>/",
        CommentDetail.as_view(),
        name="comment-detail",
    ),
    path(
        "favorites/",
        FavoriteListCreate.as_view(),
        name="favorite-list-create",
    ),
    path(
        "favorites/<int:recipe_id>/",
        FavoriteDelete.as_view(),
        name="favorite-delete",
    ),
]
