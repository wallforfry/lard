# Generated by Django 2.1.7 on 2019-02-19 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0006_auto_20190219_0022'),
    ]

    operations = [
        migrations.AddField(
            model_name='block',
            name='description',
            field=models.TextField(default='Pas de description'),
            preserve_default=False,
        ),
    ]
