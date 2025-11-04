from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True) 

    def __str__(self):
        return self.name
    
class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    difficulty = models.CharField(choices=DIFFICULTY_CHOICES, default='easy')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='recipes')
    description = models.TextField(max_length=300, blank=True)
    ingredients = models.TextField(max_length=500, help_text="List ingredients separated by comma")
    steps = models.TextField(max_length=500, help_text="Describe cooking steps")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title