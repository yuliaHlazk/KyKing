from rest_framework import serializers
from django.contrib.auth.models import User

from users_app.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("role", "bio", "avatar_url")


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "profile",
        )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=UserProfile.Role.choices,
        default=UserProfile.Role.USER,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
        )

    def create(self, validated_data):
        role = validated_data.pop("role", UserProfile.Role.USER)
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.is_active = False
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user, role=role)
        return user
