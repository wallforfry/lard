# Generated by Django 2.1.7 on 2019-05-10 14:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0008_pipelineresult'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pipelineresult',
            old_name='logss',
            new_name='logs',
        ),
    ]
