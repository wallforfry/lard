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

    def as_json(self):
        return dict(name=self.name, json_value=self.json_value, owner=self.owner, is_public=self.is_public)

class InputOutputType(models.Model):
    value = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.value

    def as_json(self):
        return dict(value=self.value)

class InputOutput(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    value = models.ForeignKey(InputOutputType, on_delete=models.SET_NULL, null=True, default=None)

    def __str__(self):
        return self.name+" : "+str(self.value)

    def as_json(self):
        return dict(name=self.name, value=self.value.as_json().get("value"))

class Block(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=False)
    code = models.TextField(default="", blank=False, null=False)
    inputs = models.ManyToManyField(InputOutput, related_name="inputs")
    outputs = models.ManyToManyField(InputOutput, related_name="outputs")

    def __str__(self):
        return self.name

    def as_json(self):
        inputs = [i.as_json() for i in self.inputs.all()]
        outputs = [o.as_json() for o in self.outputs.all()]
        return dict(name=self.name, description=self.description, code=self.code, inputs=inputs, outputs=outputs)