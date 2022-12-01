from django.contrib.postgres.fields import CICharField
from django.db import models

from users.models import User

# Create your models here.


class Tag(models.Model):
    title = CICharField(max_length=120, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Todo(models.Model):
    owner = models.ForeignKey(User, related_name='todos', on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
