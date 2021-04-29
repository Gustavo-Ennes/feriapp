# Generated by Django 2.2.4 on 2020-06-22 12:11

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20200312_0818'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinhaRelatorio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('horas_extras', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('adicional_noturno', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('faltas', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('trabalhador', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Trabalhador')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.AlterField(
            model_name='ferias',
            name='qtd_dias',
            field=models.IntegerField(choices=[(15, 'Quinze dias'), (30, 'Trinta dias')]),
        ),
        migrations.CreateModel(
            name='Relatorio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('linhas', models.ManyToManyField(to='app.LinhaRelatorio')),
                ('setor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Setor')),
            ],
        ),
    ]
