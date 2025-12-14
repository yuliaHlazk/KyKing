from __future__ import annotations

from datetime import date, timedelta

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from recipes_app.models import Recipe

from .serializers import (
    ScaleIngredientsRequestSerializer,
    SuggestRecipesRequestSerializer,
    WeeklyPlanRequestSerializer,
)
from .services.portion_scaler import split_ingredients, scale_ingredients
from .services.ingredient_matcher import split_list, recipe_missing_ingredients
from .services.openai_formatter import pretty_bullets_uk, weekly_plan_text_uk


class ScaleIngredientsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = ScaleIngredientsRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        factor = float(data["factor"])
        use_ai = bool(data.get("use_ai", False))

        if data.get("recipe_id"):
            recipe = Recipe.objects.filter(id=data["recipe_id"]).first()
            if not recipe:
                return Response(
                    {"detail": "Recipe not found."}, status=status.HTTP_404_NOT_FOUND
                )
            original_items = split_ingredients(recipe.ingredients)
        else:
            original_items = split_ingredients(data["ingredients_text"])

        scaled_items = scale_ingredients(original_items, factor)

        pretty = None
        if use_ai:
            pretty = pretty_bullets_uk("Масштабовані інгредієнти:", scaled_items)

        payload = {
            "factor": factor,
            "original_items": original_items,
            "scaled_items": scaled_items,
        }
        if pretty:
            payload["pretty"] = pretty

        return Response(payload, status=200)


class SuggestRecipesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = SuggestRecipesRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        limit = int(data.get("limit", 5))
        verified_only = bool(data.get("verified_only", True))

        if data.get("products"):
            pantry = [x.strip() for x in data["products"] if x and x.strip()]
        else:
            pantry = split_list(data["products_text"])

        qs = Recipe.objects.all()
        if verified_only:
            qs = qs.filter(verified_by_chef=True)

        results = []
        for r in qs:
            missing, matched, total = recipe_missing_ingredients(r.ingredients, pantry)
            score = 0.0 if total == 0 else matched / total
            results.append(
                {
                    "recipe_id": r.id,
                    "title": r.title,
                    "category": getattr(r.category, "name", None),
                    "difficulty": r.difficulty,
                    "score": round(score, 3),
                    "matched_count": matched,
                    "total_count": total,
                    "missing": missing,
                }
            )

        results.sort(
            key=lambda x: (x["score"], -x["matched_count"], -x["total_count"]),
            reverse=True,
        )
        results = results[:limit]

        return Response(
            {
                "products": pantry,
                "limit": limit,
                "results": results,
            },
            status=200,
        )


class WeeklyPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = WeeklyPlanRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        days = int(data.get("days", 7))
        meals_per_day = int(data.get("meals_per_day", 2))
        verified_only = bool(data.get("verified_only", True))
        use_ai = bool(data.get("use_ai", False))

        if data.get("pantry"):
            pantry = [x.strip() for x in data["pantry"] if x and x.strip()]
        else:
            pantry = split_list(data["pantry_text"])

        qs = Recipe.objects.all()
        if verified_only:
            qs = qs.filter(verified_by_chef=True)
        recipes = list(qs.order_by("-created_at"))

        if not recipes:
            recipes = list(Recipe.objects.all().order_by("-created_at"))

        if not recipes:
            return Response({"detail": "No recipes in database."}, status=400)

        plan = []
        idx = 0
        shopping_set = set()
        used = []

        start = date.today()
        for d in range(days):
            day_date = start + timedelta(days=d)
            meals = []
            for m in range(meals_per_day):
                r = recipes[idx % len(recipes)]
                idx += 1

                missing, matched, total = recipe_missing_ingredients(
                    r.ingredients, pantry
                )
                for x in missing:
                    shopping_set.add(x.strip())

                meals.append(
                    {
                        "meal": f"Meal {m+1}",
                        "recipe_id": r.id,
                        "title": r.title,
                        "missing": missing,
                        "score": round(0.0 if total == 0 else matched / total, 3),
                    }
                )
                used.append(r.id)

            plan.append(
                {
                    "date": day_date.isoformat(),
                    "meals": meals,
                }
            )

        shopping_list = sorted(shopping_set, key=lambda s: s.lower())

        payload = {
            "pantry": pantry,
            "days": days,
            "meals_per_day": meals_per_day,
            "plan": plan,
            "shopping_list": shopping_list,
            "used_recipe_ids": used,
        }

        pretty = None
        if use_ai:
            pretty = weekly_plan_text_uk(payload)
        if pretty:
            payload["pretty"] = pretty

        return Response(payload, status=200)
