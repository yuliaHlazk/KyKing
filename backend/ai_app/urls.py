from django.urls import path
from .views import ScaleIngredientsView, SuggestRecipesView, WeeklyPlanView

urlpatterns = [
    path("scale/", ScaleIngredientsView.as_view(), name="ai-scale"),
    path("suggest/", SuggestRecipesView.as_view(), name="ai-suggest"),
    path("weekly-plan/", WeeklyPlanView.as_view(), name="ai-weekly-plan"),
]
