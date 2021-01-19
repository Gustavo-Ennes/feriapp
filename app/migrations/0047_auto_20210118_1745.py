# Generated by Django 2.2.14 on 2021-01-18 20:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0046_auto_20201112_1507'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChefeDeSetor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('legenda', models.CharField(max_length=100)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('modificado', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Chefes de Setor',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Diretor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('legenda', models.CharField(max_length=100)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('modificado', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Diretores',
                'ordering': ['nome'],
            },
        ),
        migrations.AlterField(
            model_name='relatorio',
            name='ano',
            field=models.IntegerField(default=2020, validators=[django.core.validators.MaxValueValidator(2021)]),
        ),
        migrations.AlterField(
            model_name='relatorio',
            name='mes',
            field=models.IntegerField(default=12, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)]),
        ),
    ]