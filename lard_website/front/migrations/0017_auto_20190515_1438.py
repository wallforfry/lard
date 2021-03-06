# Generated by Django 2.1.7 on 2019-05-15 12:38

from django.db import migrations

def default_vote(apps, schema_editor):
    Pipeline = apps.get_model('front', 'Pipeline')
    Vote = apps.get_model('front', 'Vote')
    for p in Pipeline.objects.all():
        if not p.vote:
            p.vote = Vote.objects.create()
            p.save()

class Migration(migrations.Migration):

    dependencies = [
        ('front', '0016_auto_20190515_1438'),
    ]

    operations = [
        migrations.RunPython(default_vote)
    ]
