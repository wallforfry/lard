import datetime
import math

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils.timesince import timesince


class Vote(models.Model):
    value = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pipeline = models.ForeignKey('Pipeline', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pipeline.name + " : " + self.user.username + " : " + str(self.value)


class Pipeline(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True, default="")
    json_value = models.TextField(default="", blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=False, null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def as_json(self):
        return dict(name=self.name, json_value=self.json_value, owner=self.owner, is_public=self.is_public,
                    description=self.description)

    def score(self):
        votes = Vote.objects.filter(pipeline=self)
        value = 0
        for v in votes:
            value += v.value
        return str(value) + "/" + str(votes.count())

    def score_int(self):
        votes = Vote.objects.filter(pipeline=self)
        value = 0
        for v in votes:
            value += v.value
        return {"value": value, "count": votes.count()}

    def total_duration(self):
        prs = PipelineResult.objects.filter(pipeline=self)
        total = datetime.timedelta()
        for pr in prs:
            total += pr.updated_at - pr.created_at
        return datetime.timedelta(seconds=math.ceil(total.total_seconds()))


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
        return self.name + " : " + str(self.value)

    def as_json(self):
        return dict(name=self.name, value=self.value.as_json().get("value"))


class Block(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=False)
    code = models.TextField(default="", blank=False, null=False)
    inputs = models.ManyToManyField(InputOutput, related_name="inputs")
    outputs = models.ManyToManyField(InputOutput, related_name="outputs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def as_json(self):
        inputs = [i.as_json() for i in self.inputs.all()]
        outputs = [o.as_json() for o in self.outputs.all()]
        return dict(name=self.name, description=self.description, code=self.code, inputs=inputs, outputs=outputs)


class PipelineResult(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.SET_NULL, null=True, default=None)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=False, null=True)
    images = models.TextField(default="")
    logs = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    worker_id = models.CharField(max_length=255, blank=True, null=True, default="")

class PipelineResultImage(models.Model):
    pipeline_result = models.ForeignKey(PipelineResult, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.BinaryField(blank=True)