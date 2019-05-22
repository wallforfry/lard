# Generated by Django 2.1.7 on 2019-05-21 11:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('front', '0023_auto_20190521_1055'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scope', models.CharField(choices=[('p', 'Public'), ('f', 'Friends'), ('u', 'User')], default='Friends', max_length=1, null=True)),
                ('message', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('associated_result', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='front.PipelineResult')),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PublicationVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.Publication')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('locality', models.CharField(max_length=30, null=True)),
                ('genre', models.CharField(choices=[('m', 'Man'), ('f', 'Women'), ('o', 'Other')], max_length=1, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('friends', models.ManyToManyField(to='social.UserProfile')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='publicationvote',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.UserProfile'),
        ),
    ]