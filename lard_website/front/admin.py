from django.contrib import admin

# Register your models here.
from front.models import Pipeline, Block

admin.site.register(Pipeline)
admin.site.register(Block)