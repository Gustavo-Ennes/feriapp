# Generated by Django 2.2.14 on 2020-07-25 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0034_auto_20200725_0916'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conf',
            name='cards_colapsados',
        ),
    ]