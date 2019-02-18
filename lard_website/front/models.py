from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Pipeline(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    json_value = models.TextField(default="", blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Block(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    code = models.TextField(default="", blank=False, null=False)
    inputs = models.TextField(default="{}")
    outputs = models.TextField(default="{}")

    def __str__(self):
        return self.name