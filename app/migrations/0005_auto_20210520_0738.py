# Generated by Django 3.0.5 on 2021-05-20 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20210519_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abono',
            name='criado_em',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='abono',
            name='data',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
