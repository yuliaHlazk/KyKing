import logging

from django.contrib.auth.models import User
from rest_framework import generics, permissions, status, views, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator

from users_app.serializers import RegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        profile = getattr(user, "profile", None)
        token["username"] = user.username
        token["role"] = getattr(profile, "role", "USER")
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_active:
            logger.warning("Inactive user %s tried to login", self.user.username)
            raise serializers.ValidationError(
                "Please check your email to activate account"
            )

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        logger.info("Login attempt for user %s", username)
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            logger.info("Login successful for user %s", username)
        else:
            logger.warning(
                "Login failed for user %s (status=%s)",
                username,
                response.status_code,
            )
        return response


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info("New user registered: %s", user.username)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_path = reverse(
            "auth-activate", kwargs={"uidb64": uid, "token": token}
        )
        activation_link = self.request.build_absolute_uri(activation_path)

        subject = "Activate your account in KyKing"
        message = (
            f"Hi, {user.username}!\n"
            f"Please confirm your registration by clicking this link:\n"
            f"{activation_link}\n"
            f"If you didn’t register on KyKing, ignore this email"
        )

        send_mail(
            subject,
            message,
            getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@kyking.local"),
            [user.email],
            fail_silently=False,
        )


class ActivateAccountView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (ValueError, TypeError, UnicodeDecodeError, User.DoesNotExist):
            logger.warning("Invalid activation link was used")
            return Response(
                {"detail": "Invalid activation link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        frontend_url = getattr(settings, "FRONTEND_URL", "http://127.0.0.1:9000")
        login_url = f"{frontend_url.rstrip('/')}/login.html?activated=1"

        if user.is_active:
            return redirect(login_url)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(update_fields=["is_active"])
            logger.info("User %s activated successfully", user.username)
            return redirect(login_url)

        logger.warning("Expired or invalid activation token for user %s", user.username)
        return Response(
            {"detail": "Expired or invalid activation token"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
