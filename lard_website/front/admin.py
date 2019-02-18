from django.contrib import admin

# Register your models here.
from front.models import Pipeline, Block, InputOutputType, InputOutput

admin.site.register(Pipeline)
admin.site.register(Block)
admin.site.register(InputOutput)
admin.site.register(InputOutputType)