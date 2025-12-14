from django.contrib.auth.models import User
from rest_framework import generics, permissions

from users_app.serializers import UserSerializer
from users_app.models import UserProfile


class ChefsListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return User.objects.select_related("profile").filter(
            profile__role=UserProfile.Role.CHEF
        )


class ChefDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_url_kwarg = "chef_id"

    def get_queryset(self):
        return User.objects.select_related("profile").filter(
            profile__role=UserProfile.Role.CHEF
        )
