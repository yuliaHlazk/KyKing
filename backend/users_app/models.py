from django.db import models
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class UserProfile(models.Model):
    class Role(models.TextChoices):
        USER = "USER", "User"
        CHEF = "CHEF", "Chef"
        ADMIN = "ADMIN", "Admin"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def save(self, *args, **kwargs):
        if self.pk:
            old = UserProfile.objects.get(pk=self.pk)
            if old.role != self.role:
                logger.info(
                    "Role for user %s changed from %s to %s",
                    self.user.username,
                    old.role,
                    self.role,
                )
        else:
            logger.info(
                "UserProfile created for user %s with role %s",
                self.user.username,
                self.role,
            )
        super().save(*args, **kwargs)
