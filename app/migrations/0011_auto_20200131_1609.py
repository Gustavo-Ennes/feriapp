# Generated by Django 2.2.4 on 2020-01-31 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20200131_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setor',
            name='nome',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
