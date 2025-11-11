from rest_framework.views import APIView
from rest_framework import status
from recipes_app.models import Category, Recipe
from recipes_app.serializers import CategorySerializer, RecipeSerializer
from rest_framework.response import Response

class CategoryListCreate(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipeListCreate(APIView):
    def get(self, request):
        category_name = request.query_params.get("category", None)
        if category_name:
            recipes = Recipe.objects.filter(category__name__iexact=category_name)
        else:
            recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipeDetail(APIView):
    def get_object(self, pk):
        try:
            return Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return None

    def get(self, request, pk):
        recipe = self.get_object(pk)
        if not recipe:
            return Response({"detail": "Recipe not found"}, status=404)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data)

    def put(self, request, pk):
        recipe = self.get_object(pk)
        if not recipe:
            return Response({"detail": "Recipe not found"}, status=404)
        serializer = RecipeSerializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        recipe = self.get_object(pk)
        if not recipe:
            return Response({"detail": "Recipe not found"}, status=404)
        recipe.delete()
        return Response({"message": "Recipe deleted successfully"}, status=200)
