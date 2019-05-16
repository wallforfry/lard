# Generated by Django 2.1.7 on 2019-05-16 11:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('front', '0018_vote_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pipeline',
            name='vote',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='negative',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='positive',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='users',
        ),
        migrations.AddField(
            model_name='vote',
            name='pipeline',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='front.Pipeline'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vote',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vote',
            name='value',
            field=models.IntegerField(default=0),
        ),
    ]
