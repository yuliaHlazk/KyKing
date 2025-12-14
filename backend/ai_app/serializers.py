from rest_framework import serializers


class ScaleIngredientsRequestSerializer(serializers.Serializer):
    recipe_id = serializers.IntegerField(required=False, min_value=1)
    ingredients_text = serializers.CharField(required=False, allow_blank=False)
    factor = serializers.FloatField(required=True, min_value=0.01, max_value=100.0)
    use_ai = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        if not attrs.get("recipe_id") and not attrs.get("ingredients_text"):
            raise serializers.ValidationError("Provide either recipe_id or ingredients_text.")
        return attrs


class SuggestRecipesRequestSerializer(serializers.Serializer):
    products = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    products_text = serializers.CharField(required=False, allow_blank=False)

    limit = serializers.IntegerField(required=False, default=5, min_value=1, max_value=30)
    verified_only = serializers.BooleanField(required=False, default=True)

    def validate(self, attrs):
        if not attrs.get("products") and not attrs.get("products_text"):
            raise serializers.ValidationError("Provide either products (list) or products_text (string).")
        return attrs


class WeeklyPlanRequestSerializer(serializers.Serializer):
    pantry = serializers.ListField(child=serializers.CharField(), required=False)
    pantry_text = serializers.CharField(required=False, allow_blank=False)

    days = serializers.IntegerField(required=False, default=7, min_value=1, max_value=14)
    meals_per_day = serializers.IntegerField(required=False, default=2, min_value=1, max_value=3)

    verified_only = serializers.BooleanField(required=False, default=True)
    use_ai = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        if not attrs.get("pantry") and not attrs.get("pantry_text"):
            raise serializers.ValidationError("Provide either pantry (list) or pantry_text (string).")
        return attrs