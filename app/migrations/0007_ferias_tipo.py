# Generated by Django 2.2.4 on 2019-12-20 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20191216_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='ferias',
            name='tipo',
            field=models.CharField(default='f', editable=False, max_length=2),
        ),
    ]
