# Generated by Django 2.1.7 on 2019-05-21 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0005_auto_20190521_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='friends',
            field=models.ManyToManyField(blank=True, null=True, to='social.UserProfile'),
        ),
    ]