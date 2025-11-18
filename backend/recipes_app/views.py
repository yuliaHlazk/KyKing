import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)

from recipes_app.models import Category, Recipe, Comment, Favorite
from recipes_app.serializers import (
    CategorySerializer,
    RecipeSerializer,
    CommentSerializer,
    FavoriteSerializer,
)

from users_app.models import UserProfile
from recipes_app.permissions import (
    RoleRequired,
    IsAuthorOrAdmin,
    IsFavoriteOwnerOrAdmin,
    IsChefOrAdmin,
)

logger = logging.getLogger(__name__)


class CategoryListCreate(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [RoleRequired(["ADMIN"])]

    def get(self, request):
        categories = Category.objects.all().order_by("name")
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            logger.info(
                "Category created id=%s name=%s",
                category.id,
                category.name,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [RoleRequired(["ADMIN"])]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response(
                {"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response(
                {"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            logger.info(
                "Category updated: id=%s name=%s",
                category.id,
                category.name,
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response(
                {"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND
            )
        logger.info(
            "Category deleted id=%s name=%s",
            category.id,
            category.name,
        )
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeListCreate(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated()]

    def get(self, request):
        
        qs = Recipe.objects.select_related("author", "category").all()

        category_slug = request.query_params.get("category")
        difficulty = request.query_params.get("difficulty")
        search = request.query_params.get("search")
        verified = request.query_params.get("verified")

        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        if difficulty:
            qs = qs.filter(difficulty=difficulty)

        if verified is not None:
            v = verified.lower()
            if v in ("true", "1", "yes"):
                qs = qs.filter(verified_by_chef=True)
            elif v in ("false", "0", "no"):
                qs = qs.filter(verified_by_chef=False)

        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(
                description__icontains=search
            )

        serializer = RecipeSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = RecipeSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            recipe = serializer.save()
            logger.info(
                "Recipe created via API: id=%s title=%s user=%s",
                recipe.id,
                recipe.title,
                request.user.username,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipeDetail(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthorOrAdmin()]

    def get_object(self, pk):
        try:
            return Recipe.objects.select_related("author", "category").get(pk=pk)
        except Recipe.DoesNotExist:
            return None

    def get(self, request, pk):
        recipe = self.get_object(pk)
        if not recipe:
            return Response(
                {"detail": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = RecipeSerializer(recipe, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk):
        recipe = self.get_object(pk)
        if not recipe:
            return Response(
                {"detail": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, recipe)

        serializer = RecipeSerializer(
            recipe,
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            recipe = serializer.save()
            logger.info(
                "Recipe updated id=%s title=%s user=%s",
                recipe.id,
                recipe.title,
                request.user.username,
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        recipe = self.get_object(pk)
        if not recipe:
            return Response(
                {"detail": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, recipe)

        logger.info(
            "Recipe deleted id=%s title=%s user=%s",
            recipe.id,
            recipe.title,
            request.user.username,
        )
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeVerify(APIView):

    permission_classes = [IsChefOrAdmin]

    def post(self, request, pk):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(
                {"detail": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )

        self.check_permissions(request)

        recipe.verified_by_chef = True
        recipe.save()

        logger.info(
            "Recipe verified by chef id=%s title=%s user=%s",
            recipe.id,
            recipe.title,
            request.user.username,
        )

        serializer = RecipeSerializer(recipe, context={"request": request})
        return Response(serializer.data)


class CommentListCreate(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated()]

    def get(self, request, recipe_id):
        comments = Comment.objects.filter(recipe_id=recipe_id).select_related(
            "author", "recipe"
        )
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, recipe_id):
        data = request.data.copy()
        data["recipe"] = recipe_id

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            comment = serializer.save(author=request.user)
            logger.info(
                "Comment created: id=%s recipe=%s user=%s",
                comment.id,
                recipe_id,
                request.user.username,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetail(APIView):

    permission_classes = [IsAuthorOrAdmin]

    def get_object(self, pk):
        try:
            return Comment.objects.select_related("author", "recipe").get(pk=pk)
        except Comment.DoesNotExist:
            return None

    def delete(self, request, pk):
        comment = self.get_object(pk)
        if not comment:
            return Response(
                {"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, comment)

        logger.info(
            "Comment deleted id=%s recipe=%s user=%s",
            comment.id,
            comment.recipe_id,
            request.user.username,
        )
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteListCreate(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        profile = getattr(request.user, "profile", None)
        qs = Favorite.objects.select_related("recipe", "user")

        if profile and profile.role == UserProfile.Role.ADMIN:
            user_id = request.query_params.get("user")
            if user_id:
                qs = qs.filter(user_id=user_id)
            else:
                qs = qs.filter(user=request.user)
        else:
            qs = qs.filter(user=request.user)

        serializer = FavoriteSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        recipe_id = request.data.get("recipe")
        if not recipe_id:
            return Response(
                {"detail": "recipe is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            recipe_id=recipe_id,
        )

        if created:
            logger.info(
                "Favorite created: id=%s recipe=%s user=%s",
                favorite.id,
                recipe_id,
                request.user.username,
            )

        serializer = FavoriteSerializer(favorite)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class FavoriteDelete(APIView):

    permission_classes = [IsAuthenticated, IsFavoriteOwnerOrAdmin]

    def delete(self, request, recipe_id):
        try:
            favorite = Favorite.objects.get(
                user=request.user,
                recipe_id=recipe_id,
            )
        except Favorite.DoesNotExist:
            return Response(
                {"detail": "Favorite not found"}, status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, favorite)

        logger.info(
            "Favorite deleted: id=%s recipe=%s user=%s",
            favorite.id,
            recipe_id,
            request.user.username,
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
