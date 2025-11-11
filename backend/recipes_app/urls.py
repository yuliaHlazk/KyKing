from django.urls import path
from recipes_app.views import CategoryListCreate, RecipeListCreate, RecipeDetail

urlpatterns = [
    path('categories/', CategoryListCreate.as_view(), name='category-list-create'),
    path('recipes/', RecipeListCreate.as_view(), name='recipe-list-create'),
    path('recipes/<int:pk>/', RecipeDetail.as_view(), name='recipe-detail'),
]
