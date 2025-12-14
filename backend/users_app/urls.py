from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users_app.views import (
    MyTokenObtainPairView,
    RegisterView,
    MeView,
    ActivateAccountView,
)
from users_app.views_chefs import ChefsListView, ChefDetailView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path(
        "activate/<str:uidb64>/<str:token>/",
        ActivateAccountView.as_view(),
        name="auth-activate",
    ),
    path("token/", MyTokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("chefs/", ChefsListView.as_view(), name="chef-list"),
    path("chefs/<int:chef_id>/", ChefDetailView.as_view(), name="chef-detail"),
]
