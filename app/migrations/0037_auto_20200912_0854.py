# Generated by Django 2.2.14 on 2020-09-12 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0036_auto_20200912_0726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='descricao',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='banner',
            name='link_img',
            field=models.URLField(unique=True),
        ),
        migrations.AlterField(
            model_name='banner',
            name='titulo',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
