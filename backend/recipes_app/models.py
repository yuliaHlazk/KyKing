from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
    )

    title = models.CharField(max_length=200)
    difficulty = models.CharField(choices=DIFFICULTY_CHOICES, default="easy")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="recipes"
    )
    description = models.TextField(max_length=300, blank=True)
    ingredients = models.TextField(
        max_length=500, help_text="List ingredients separated by comma"
    )
    steps = models.TextField(max_length=500, help_text="Describe cooking steps")
    created_at = models.DateTimeField(auto_now_add=True)
    verified_by_chef = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        from users_app.models import UserProfile

        is_new = self.pk is None
        previous_verified = None

        if not is_new:
            try:
                previous = Recipe.objects.get(pk=self.pk)
                previous_verified = previous.verified_by_chef
            except Recipe.DoesNotExist:
                previous_verified = None

        if is_new and self.author_id:
            profile = getattr(self.author, "profile", None)
            if profile and profile.role in [
                UserProfile.Role.CHEF,
                UserProfile.Role.ADMIN,
            ]:
                self.verified_by_chef = True

        super().save(*args, **kwargs)

        if is_new:
            logger.info(
                "Recipe created: id=%s, title=%s, author=%s, verified_by_chef=%s",
                self.pk,
                self.title,
                self.author.username,
                self.verified_by_chef,
            )
        else:
            logger.info(
                "Recipe updated: id=%s, title=%s, author=%s, verified_by_chef=%s",
                self.pk,
                self.title,
                self.author.username,
                self.verified_by_chef,
            )

        should_notify = (
            not is_new and previous_verified is False and self.verified_by_chef is True
        )

        if should_notify and self.author.email:
            try:
                frontend_url = getattr(
                    settings, "FRONTEND_URL", "http://127.0.0.1:9000"
                )
                recipe_link = (
                    f"{frontend_url.rstrip('/')}/recipe_detail.html?recipe={self.pk}"
                )

                subject = "KyKing about your recipe"
                message = (
                    f"Hello, {self.author.username}!\n"
                    f"Your recipe «{self.title}» was approved by chef✅\n"
                    f"See your recipe: {recipe_link}\n"
                    "With love, KyKing!"
                )

                send_mail(
                    subject,
                    message,
                    getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@kyking.local"),
                    [self.author.email],
                    fail_silently=True,
                )

                logger.info(
                    "Approval email sent to user=%s for recipe id=%s",
                    self.author.username,
                    self.pk,
                )
            except Exception:
                logger.exception(
                    "Failed to send approval email for recipe id=%s", self.pk
                )


class Comment(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    is_chef_comment = models.BooleanField(default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.recipe.title}"

    class Meta:
        ordering = ["-is_chef_comment", "-created_at"]

    def save(self, *args, **kwargs):
        from users_app.models import UserProfile

        profile = getattr(self.author, "profile", None)
        self.is_chef_comment = bool(profile and profile.role == UserProfile.Role.CHEF)

        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            logger.info(
                "Comment created id=%s on recipe=%s by user %s (chef=%s)",
                self.pk,
                self.recipe_id,
                self.author.username,
                self.is_chef_comment,
            )
        else:
            logger.info(
                "Comment updated id=%s on recipe=%s by user %s (chef=%s)",
                self.pk,
                self.recipe_id,
                self.author.username,
                self.is_chef_comment,
            )


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Favorite {self.user.username} - {self.recipe.title}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_recipe_favorite"
            )
        ]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            logger.info(
                "Favorite created id=%s user=%s recipe=%s",
                self.pk,
                self.user.username,
                self.recipe_id,
            )

    def delete(self, *args, **kwargs):
        logger.info(
            "Favorite deleted id=%s user=%s recipe=%s",
            self.pk,
            self.user.username,
            self.recipe_id,
        )
        return super().delete(*args, **kwargs)
