from rest_framework import serializers
from recipes_app.models import Category, Comment, Favorite, Recipe


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class RecipeSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "title",
            "description",
            "ingredients",
            "steps",
            "difficulty",
            "category",
            "category_name",
            "author",
            "author_username",
            "verified_by_chef",
            "created_at",
            "is_favorite",
        )
        read_only_fields = ("author", "verified_by_chef", "created_at")

    def get_is_favorite(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return obj.favorited_by.filter(user=user).exists()

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["author"] = request.user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    is_chef_comment = serializers.BooleanField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "recipe",
            "author",
            "author_username",
            "text",
            "is_chef_comment",
            "created_at",
        )
        read_only_fields = ("author", "is_chef_comment", "created_at")


class FavoriteSerializer(serializers.ModelSerializer):
    recipe_title = serializers.CharField(source="recipe.title", read_only=True)

    class Meta:
        model = Favorite
        fields = ("id", "user", "recipe", "recipe_title", "created_at")
        read_only_fields = ("user", "created_at")

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["user"] = request.user
        return super().create(validated_data)
