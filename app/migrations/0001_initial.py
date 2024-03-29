# Generated by Django 3.0.5 on 2021-05-19 14:26

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Abono',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expediente', models.CharField(choices=[('matutino', 'Matutino'), ('vespertino', 'Vespertino'), ('integral', 'Integral')], max_length=20)),
                ('data', models.DateField()),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('modificado_em', models.DateTimeField(auto_now=True)),
                ('deferido', models.BooleanField(default=False, editable=False)),
                ('observacoes', models.TextField(blank=True, editable=False)),
                ('fruido', models.BooleanField(default=False, editable=False)),
                ('criado_por', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['data'],
            },
        ),
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(blank=True, max_length=200)),
                ('descricao', models.TextField(blank=True)),
                ('link_img', models.URLField(unique=True)),
                ('link', models.URLField()),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('modificado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-criado_em'],
            },
        ),
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
            name='Conf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proximas_folgas', models.BooleanField(default=True, help_text='Mostra uma tabela na página principal, representando os trabalhadores que tem as folgas próximas')),
                ('em_andamento', models.BooleanField(default=True, help_text='Mostra uma tabela na página principal, representando os trabalhadores que estão de folga no momento')),
                ('proximos_retornos', models.BooleanField(default=True, help_text='Mostra uma tabela na página principal, representando os trabalhadores que estão no final de sua folga ')),
                ('calculo_de_adicional', models.BooleanField(default=False, help_text='Multiplica o total de horas por 1,143, caso marcado', verbose_name='Cálculo de Adicional Noturno')),
            ],
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
        migrations.CreateModel(
            name='Ferias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qtd_dias', models.IntegerField(choices=[(15, 'Quinze dias'), (30, 'Trinta dias')])),
                ('data_inicio', models.DateField()),
                ('data_termino', models.DateField(editable=False)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('modificado_em', models.DateTimeField(auto_now=True)),
                ('deferida', models.BooleanField(default=False, editable=False)),
                ('observacoes', models.TextField(blank=True, editable=False)),
                ('tipo', models.CharField(default='f', editable=False, max_length=2)),
                ('fruida', models.BooleanField(default=False, editable=False)),
                ('criado_por', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Férias',
                'verbose_name_plural': 'Férias',
                'ordering': ['data_inicio'],
            },
        ),
        migrations.CreateModel(
            name='Lembrete',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('mensagem', models.TextField()),
                ('url_name', models.CharField(max_length=100)),
                ('periodicidade', models.CharField(choices=[('d', 'Diário'), ('s', 'Semanal'), ('m', 'Mensal')], max_length=2)),
                ('dia', models.IntegerField(help_text='Semanal: indique o dia da semana(0=domingo, 1=segunda,...). Mensal: caso não haja tal dia em algum mês(30, 31), o lembrete será exibido no último dia do mês', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(31)])),
                ('mostrado_esse_mes', models.BooleanField(default=False)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('modificado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['dia'],
            },
        ),
        migrations.CreateModel(
            name='LinhaRelatorio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('horas_extras', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('adicional_noturno', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('faltas', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('modificado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Linha de Relatório',
                'verbose_name_plural': 'Linhas de Relatório',
                'ordering': ['trabalhador__nome'],
            },
        ),
        migrations.CreateModel(
            name='Setor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('modificado_em', models.DateTimeField(auto_now=True)),
                ('criado_por', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Setores',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='LicencaPremio',
            fields=[
                ('ferias_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.Ferias')),
            ],
            options={
                'verbose_name': 'Licenças Prêmio',
                'verbose_name_plural': 'Licença Prêmio',
                'ordering': ['data_inicio'],
            },
            bases=('app.ferias',),
        ),
        migrations.CreateModel(
            name='Trabalhador',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('matricula', models.CharField(max_length=15, unique=True)),
                ('registro', models.CharField(max_length=15, unique=True)),
                ('funcao', models.CharField(max_length=50)),
                ('data_admissao', models.DateTimeField()),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('modificado_em', models.DateTimeField(auto_now=True)),
                ('situacao', models.CharField(choices=[('ferias', 'Férias'), ('licenca', 'Licença-prêmio'), ('abono', 'Abono'), ('ativo', 'Ativo'), ('atestado', 'Atestado Médico')], max_length=100)),
                ('rg', models.CharField(blank=True, max_length=20, null=True)),
                ('ctps', models.CharField(blank=True, max_length=20, null=True)),
                ('cpf', models.CharField(blank=True, max_length=20, null=True)),
                ('ctps_serie', models.CharField(blank=True, max_length=20, null=True)),
                ('criado_por', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('setor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Setor')),
                ('user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuario', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Trabalhadores',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Relatorio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(default='vazio', max_length=100)),
                ('num_oficio', models.CharField(max_length=10)),
                ('mes', models.IntegerField(default=4, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)])),
                ('ano', models.IntegerField(default=2021, validators=[django.core.validators.MaxValueValidator(2021)])),
                ('data_fechamento', models.DateField(blank=True, null=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('modificado_em', models.DateTimeField(auto_now=True)),
                ('linhas', models.ManyToManyField(blank=True, to='app.LinhaRelatorio')),
                ('setor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Setor')),
            ],
            options={
                'verbose_name': 'Relatório',
                'verbose_name_plural': 'Relatórios',
                'ordering': ['-criado_em', 'setor__nome'],
            },
        ),
        migrations.CreateModel(
            name='RelacaoAbono',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_inicio', models.DateTimeField()),
                ('data_termino', models.DateTimeField()),
                ('abonos', models.ManyToManyField(blank=True, to='app.Abono')),
            ],
            options={
                'verbose_name': 'Relação de abonos',
                'verbose_name_plural': 'Relações de abonos',
                'ordering': ['-data_inicio'],
            },
        ),
        migrations.AddField(
            model_name='linharelatorio',
            name='trabalhador',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Trabalhador'),
        ),
        migrations.AddField(
            model_name='ferias',
            name='trabalhador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Trabalhador'),
        ),
        migrations.AddField(
            model_name='abono',
            name='trabalhador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Trabalhador'),
        ),
    ]
