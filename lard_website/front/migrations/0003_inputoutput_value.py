# Generated by Django 2.1.7 on 2019-02-18 22:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0002_remove_inputoutput_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='inputoutput',
            name='value',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='front.InputOutputType'),
        ),
    ]
