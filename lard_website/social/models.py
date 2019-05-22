from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

# Create your models here.
from front.models import PipelineResult, Pipeline, PipelineResultImage


class UserProfile(models.Model):
    GENRE_CHOICES = (
        ('m', 'Man'),
        ('f', 'Women'),
        ('o', 'Other'),
    )

    SCOPE_CHOICES = (
        ('p', 'Public'),
        ('f', 'Friends'),
        ('u', 'User'),
    )

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=255)
    locality = models.CharField(max_length=30, null=True, blank=True)
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES, null=True, blank=True)
    scope = models.CharField(max_length=1, choices=SCOPE_CHOICES, null=True, default=SCOPE_CHOICES[0][0])
    followings = models.ManyToManyField('UserProfile', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_friend(self, user_profile):
        self.followings.add(user_profile)

    def remove_friend(self, user_profile):
        self.followings.remove(user_profile)

    def get_publications(self):
        return Publication.objects.filter(user_profile=self)

    def get_pipelines(self):
        return Pipeline.objects.filter(owner=self.user)

    def get_results(self):
        return PipelineResult.objects.filter(user=self.user)

    def get_followers(self):
        return UserProfile.objects.filter(followings=self)

    def get_gender(self):
        i = None
        for e in self.GENRE_CHOICES:
            if self.genre == e[0]:
                i = e
                break
        return i

    def get_scope(self):
        i = None
        for e in self.SCOPE_CHOICES:
            if self.scope == e[0]:
                i = e
                break
        return i

    def __str__(self):
        return self.username


class Publication(models.Model):
    SCOPE_CHOICES = (
        ('p', 'Public'),
        ('f', 'Friends'),
        ('u', 'User'),
    )

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    scope = models.CharField(max_length=1, choices=SCOPE_CHOICES, null=True, default=SCOPE_CHOICES[1][0])
    message = models.TextField(blank=True, default="")
    associated_result = models.ForeignKey(PipelineResult, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_publication_score(self):
        pv = PublicationVote.objects.filter(publication=self)
        sum = 0
        for v in pv:
            sum += v.value
        return sum

    def get_images(self):
        return PipelineResultImage.objects.filter(pipeline_result=self.associated_result)

    def get_likers(self):
        return UserProfile.objects.filter(publicationvote__publication=self, publicationvote__value__gt=0)

    def __str__(self):
        return self.message


class PublicationVote(models.Model):
    value = models.IntegerField(default=0)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def create_user_profile(sender, instance, created, **kwargs):
    up = UserProfile.objects.get_or_create(user=instance)[0]
    up.username = instance.username
    up.save()


post_save.connect(create_user_profile, sender=User)
