# Generated by Django 2.2.14 on 2020-11-12 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0044_auto_20201112_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abono',
            name='expediente',
            field=models.CharField(choices=[('matutino', 'Matutino'), ('vespertino', 'Vespertino'), ('integral', 'Integral')], max_length=1),
        ),
    ]