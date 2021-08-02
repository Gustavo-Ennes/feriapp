# Generated by Django 3.0.5 on 2021-07-30 11:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20210520_0948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relatorio',
            name='mes',
            field=models.IntegerField(default=6, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)]),
        ),
    ]
