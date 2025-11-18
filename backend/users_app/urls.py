from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users_app.views import MyTokenObtainPairView, RegisterView, MeView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("token/", MyTokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
]