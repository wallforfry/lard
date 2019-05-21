from django.contrib import admin

# Register your models here.
from social.models import UserProfile, Publication, PublicationVote

admin.site.register(UserProfile)
admin.site.register(Publication)
admin.site.register(PublicationVote)
