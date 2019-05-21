from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

# Create your models here.
from front.models import PipelineResult


class UserProfile(models.Model):
    GENRE_CHOICES = (
        ('m', 'Man'),
        ('f', 'Women'),
        ('o', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=255)
    locality = models.CharField(max_length=30, null=True)
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES, null=True)
    friends = models.ManyToManyField('UserProfile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_friend(self, user_profile):
        self.friends.add(user_profile)

    def remove_friend(self, user_profile):
        self.friends.remove(user_profile)

    def __str__(self):
        return self.username

class Publication(models.Model):
    SCOPE_CHOICES = (
        ('p', 'Public'),
        ('f', 'Friends'),
        ('u', 'User'),
    )

    user_profile = models.ForeignKey(User, on_delete=models.CASCADE)
    scope = models.CharField(max_length=1, choices=SCOPE_CHOICES, null=True, default=SCOPE_CHOICES[1][1])
    message = models.TextField(blank=True, default="")
    associated_result = models.ForeignKey(PipelineResult, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_publication_score(self):
        pv = PublicationVote.objects.filter(publication=self)
        sum = 0
        for v in pv:
            sum += v.value
        return sum

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