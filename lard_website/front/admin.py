from django.contrib import admin

# Register your models here.
from front.models import Pipeline, Block, InputOutputType, InputOutput, PipelineResult, Vote, PipelineResultImage


class PipelineResultAdmin(admin.ModelAdmin):
    search_fields = ('pipeline', 'user', 'created_at', 'updated_at')
    list_display = ('pipeline', 'user', 'created_at', 'updated_at', 'worker_id')
    list_filter = ('user', 'pipeline')


admin.site.register(Pipeline)
admin.site.register(Vote)
admin.site.register(PipelineResult, PipelineResultAdmin)
admin.site.register(PipelineResultImage)
admin.site.register(Block)
admin.site.register(InputOutput)
admin.site.register(InputOutputType)