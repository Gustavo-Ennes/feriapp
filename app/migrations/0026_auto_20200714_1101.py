# Generated by Django 2.2.4 on 2020-07-14 14:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_auto_20200714_1049'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='linharelatorio',
            options={'ordering': ['trabalhador__nome'], 'verbose_name': 'Linha de Relatório', 'verbose_name_plural': 'Linhas de Relatório'},
        ),
    ]