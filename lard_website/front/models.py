from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Pipeline(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    json_value = models.TextField(default="", blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=False, null=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class InputOutputType(models.Model):
    value = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.value

class InputOutput(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    value = models.ForeignKey(InputOutputType, on_delete=models.SET_NULL, null=True, default=None)

    def __str__(self):
        return self.name+" : "+str(self.value)

class Block(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    code = models.TextField(default="", blank=False, null=False)
    inputs = models.ManyToManyField(InputOutput, related_name="inputs")
    outputs = models.ManyToManyField(InputOutput, related_name="outputs")

    def __str__(self):
        return self.name
