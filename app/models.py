from django.db import models
from datetime import datetime, timedelta
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from bs4 import BeautifulSoup as bs
import random
import traceback

# Create your models here.


class Setor(models.Model):
    objects = models.Manager()
    nome = models.CharField(max_length=100, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s - desde %s' % (self.nome, self.criado_em.strftime("%d/%m/%Y"))

    def get_absolute_url(self):
        return reverse('setor')

    class Meta:
        verbose_name_plural = 'Setores'
        ordering = ['nome']


class Trabalhador(models.Model):
    objects = models.Manager()
    OPCOES = (
        ('ferias', "Férias"),
        ('licenca', "Licença-prêmio"),
        ('abono', "Abono"),
        ('ativo', "Ativo"),
        ('atestado', "Atestado Médico"),
    )

    nome = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuario',
                             editable=False)
    matricula = models.CharField(unique=True, max_length=15)
    registro = models.CharField(unique=True, max_length=15)
    funcao = models.CharField(max_length=50)
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True)
    data_admissao = models.DateTimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)
    situacao = models.CharField(max_length=100, choices=OPCOES)
    rg = models.CharField(max_length=20, blank=True, null=True)
    ctps = models.CharField(max_length=20, blank=True, null=True)
    cpf = models.CharField(max_length=20, blank=True, null=True)
    ctps_serie = models.CharField(max_length=20, blank=True, null=True)
    criado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, editable=False, null=True, blank=True)

    def __str__(self):
        return '%s : %s - %s - desde %s' % (
            self.nome, self.funcao, self.setor.nome, self.data_admissao.strftime("%d/%m/%Y"))

    def save(self, *args, **kwargs):
        if not self.user:
            self.user = User.objects.create_user(
                username=self.nome.replace(" ", ""), password=self.registro)

        super(Trabalhador, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('trabalhadores')

    class Meta:
        verbose_name_plural = 'Trabalhadores'
        ordering = ['nome']


class Ferias(models.Model):
    OPCOES = (
        (15, "Quinze dias"),
        (30, "Trinta dias"),
    )

    objects = models.Manager()

    class FeriasFruidas(models.Manager):
        def all(self):
            return super().get_queryset().filter(
                Q(tipo='f') & Q(data_termino__lt=timezone.now().date()) & Q(deferida=True))

    class FeriasIndeferidas(models.Manager):
        def all(self):
            return super().get_queryset().filter(Q(tipo='f') & Q(deferida=False))

    class FeriasEmAndamento(models.Manager):
        def all(self):
            return super().get_queryset().filter(Q(tipo='f') & Q(data_inicio__lte=timezone.now().date()) & Q(
                data_termino__gte=timezone.now().date()) & Q(deferida=True))

    fruidas = FeriasFruidas()
    indeferidas = FeriasIndeferidas()
    em_andamento = FeriasEmAndamento()

    trabalhador = models.ForeignKey(Trabalhador, on_delete=models.CASCADE)
    qtd_dias = models.IntegerField(choices=OPCOES)
    data_inicio = models.DateField()
    data_termino = models.DateField(editable=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)
    deferida = models.BooleanField(editable=False, default=False)
    observacoes = models.TextField(blank=True, editable=False)
    tipo = models.CharField(max_length=2, default='f', editable=False)
    fruida = models.BooleanField(editable=False, default=False)
    criado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, editable=False, null=True, blank=True)

    def save(self, validacao=True, *args, **kwargs):

        self.data_termino = self.data_inicio + \
            timedelta(days=self.qtd_dias - 1)

        if not validacao:
            self.deferida = False
        else:
            self.deferida = valida_ferias(self)

        super(Ferias, self).save(*args, **kwargs)

    def __str__(self):
        return '%d dias - %s -saindo %s' % (self.qtd_dias, self.trabalhador.nome, self.data_inicio.strftime("%d/%m/%Y"))

    def get_absolute_url(self):
        return reverse('ferias')

    class Meta:
        verbose_name_plural = "Férias"
        verbose_name = "Férias"
        ordering = ['data_inicio']


class LicencaPremio(Ferias):
    OPCOES = (
        (15, "Quinze dias"),
        (30, "Trinta dias"),
        (45, "Quarenta e cinco dias"),
        (60, "Sessenta dias"),
        (75, "Setenta e cinco dias"),
        (90, "Noventa dias")
    )

    objects = models.Manager()

    class LicencasFruidas(models.Manager):
        def all(self):
            return super().get_queryset().filter(Q(data_termino__lt=timezone.now().date()) & Q(deferida=True))

    class LicencasIndeferidas(models.Manager):
        def all(self):
            return super().get_queryset().filter(Q(deferida=False))

    class LicencaEmAndamento(models.Manager):
        def all(self):
            return super().get_queryset().filter(Q(data_inicio__lte=timezone.now().date()) & Q(deferida=True) & Q(
                data_termino__gte=timezone.now().date()))

    fruidas = LicencasFruidas()
    indeferidas = LicencasIndeferidas()
    em_andamento = LicencaEmAndamento()

    def __str__(self):
        return '%d dias - %s -saindo %s' % (self.qtd_dias, self.trabalhador.nome, self.data_inicio.strftime("%d/%m/%Y"))

    def save(self, validacao=True, *args, **kwargs):

        self.data_termino = self.data_inicio + \
            timedelta(days=self.qtd_dias - 1)
        self.tipo = 'l'

        if not validacao:
            self.deferida = False
        else:
            self.deferida = valida_ferias(self)

        super(LicencaPremio, self).save(validacao, *args, **kwargs)

    def get_absolute_url(self):
        return reverse('licenca_premio')

    class Meta:
        verbose_name_plural = "Licença Prêmio"
        verbose_name = "Licenças Prêmio"
        ordering = ['data_inicio']


class Abono(models.Model):

    expedientes_opt = [
        ('matutino', 'Matutino'),
        ('vespertino', 'Vespertino'),
        ('integral', 'Integral'),
    ]
    objects = models.Manager()

    class AbonosFruidos(models.Manager):
        def all(self):
            return super().get_queryset().filter(Q(data__lt=timezone.now().date()) & Q(deferido=True))

    class AbonosIndeferidos(models.Manager):
        def all(self):
            return super().get_queryset().filter(Q(deferido=False))

    class AbonoEmAndamento(models.Manager):
        def all(self):
            return super().get_queryset().filter(Q(data=timezone.now().date()) & Q(deferido=True))

    fruidos = AbonosFruidos()
    indeferidos = AbonosIndeferidos()
    em_andamento = AbonoEmAndamento()

    trabalhador = models.ForeignKey(Trabalhador, on_delete=models.CASCADE)
    expediente = models.CharField(choices=expedientes_opt, max_length=20)
    data = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)
    deferido = models.BooleanField(editable=False, default=False)
    observacoes = models.TextField(blank=True, editable=False)
    fruido = models.BooleanField(editable=False, default=False)
    criado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, editable=False, null=True, blank=True)

    def is_this_month(self):
        data = timezone.now().date()
        if self.data:
            return ((data.month == self.data.month) and (data.year == self.data.year))
        return False

    # form=false representa que eu não quero salvar a instaância quando salvo o form porque adiciono um campo
    def save(self, validacao=True, *args, **kwargs):

        if validacao:
            self.deferido = valida_abono2(self)
        super(Abono, self).save(*args, **kwargs)

    def __str__(self):
        return '%s: %s - %s' % (self.id, self.trabalhador.nome, self.data.strftime("%d/%m/%Y"))

    def get_absolute_url(self):
        return reverse('abono')

    class Meta:
        ordering = ['data']


class Conf(models.Model):
    ADC_CONST = 1.143
    objects = models.Manager()

    proximas_folgas = models.BooleanField(
        default=True,
        help_text='Mostra uma tabela na página principal, representando os trabalhadores que tem as folgas próximas'
    )
    em_andamento = models.BooleanField(
        default=True,
        help_text='Mostra uma tabela na página principal, representando os trabalhadores que estão de folga no momento'
    )
    proximos_retornos = models.BooleanField(
        default=True,
        help_text='Mostra uma tabela na página principal, representando os trabalhadores que estão no final de sua '
                  'folga '
    )
    calculo_de_adicional = models.BooleanField(
        default=False,
        verbose_name="Cálculo de Adicional Noturno",
        help_text='Multiplica o total de horas por 1,143, caso marcado'
    )


class Diretor(models.Model):
    objects = models.Manager()
    nome = models.CharField(max_length=200)
    legenda = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Diretores"
        ordering = ['nome']


class ChefeDeSetor(models.Model):
    objects = models.Manager()
    nome = models.CharField(max_length=200)
    legenda = models.CharField(max_length=100)
    rg = models.CharField(max_length=20)
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Chefes de Setor"
        ordering = ['nome']


class Lembrete(models.Model):
    options = [
        ('d', 'Diário'),
        ('s', 'Semanal'),
        ('m', 'Mensal'),
    ]

    objects = models.Manager()
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    url_name = models.CharField(max_length=100)
    periodicidade = models.CharField(max_length=2, choices=options)
    dia = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Semanal: indique o dia da semana(0=domingo, 1=segunda,...). Mensal: caso não haja tal dia em algum mês(30, 31), o lembrete será exibido no último dia do mês"
    )
    mostrado_esse_mes = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    @property
    def is_valid(self):
        is_valid = False
        hoje = timezone.now()
        weekday = hoje.weekday()
        if not self.mostrado_esse_mes:
            # aqui a lógica muda dependendo da periodicidade
            if self.periodicidade == 'm':
                if weekday >= self.dia:
                    is_valid = True
            elif self.periodicidade == 's':
                if self.dia <= weekday < 6:
                    is_valid = True
            elif self.periodicidade == 'd':
                if hoje.hour == self.day:
                    is_valid = True
        return is_valid

    class Meta:
        ordering = ['dia']


class Banner(models.Model):

    objects = models.Manager()
    titulo = models.CharField(max_length=200, blank=True)
    descricao = models.TextField(blank=True)
    link_img = models.URLField(unique=True)
    link = models.URLField()
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']

    def get_absolute_url(self):
        return reverse('banner')


class LinhaRelatorio(models.Model):
    objects = models.Manager()
    trabalhador = models.ForeignKey(
        Trabalhador, on_delete=models.SET_NULL, null=True)
    horas_extras = models.FloatField(
        default=0, validators=[MinValueValidator(0)])
    adicional_noturno = models.FloatField(
        default=0, validators=[MinValueValidator(0)])
    faltas = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    dias_faltas = []
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        try:
            return "%s(%.1f, %.1f, %d)" % (self.trabalhador.nome, self.horas_extras, self.adicional_noturno, self.faltas)
        except:
            return "Trabalhador excluído(%.1f, %.1f, %d)" % (self.horas_extras, self.adicional_noturno, self.faltas)

    class Meta:
        ordering = ['trabalhador__nome']
        verbose_name = "Linha de Relatório"
        verbose_name_plural = 'Linhas de Relatório'

    @staticmethod
    def transferencia(relatorio_fonte, relatorio_alvo, linha):
        if relatorio_fonte and relatorio_alvo and linha:
            if linha in relatorio_fonte.linhas.all():
                try:
                    relatorio_fonte.linhas.remove(linha)
                    relatorio_alvo.linhas.add(linha)
                    relatorio_fonte.save()
                    relatorio_alvo.save()
                except Exception as e:
                    print("Erro: %s" % e)


def mes_anterior():
    data = datetime.now()
    return data.month - 1 if data.month > 1 else 12


def ano_padrao():
    data = datetime.now()
    return data.year - 1 if data.month == 1 else data.year


class Relatorio(models.Model):
    objects = models.Manager()

    class Vigente(models.Manager):
        def all(self):
            data = datetime.now()
            return super().get_queryset().filter(
                Q(mes=data.month - 1 if data.month != 1 else 12)
                & Q(ano=data.year if data.month != 1 else data.year - 1)
                & (Q(estado='terminado') | Q(estado='oficial'))
            )

        def em_aberto(self):
            data = datetime.now()
            return super().get_queryset().filter(
                Q(mes=data.month - 1 if data.month != 1 else 12)
                & Q(ano=data.year if data.month != 1 else data.year - 1)
                & (Q(estado='terminado') | Q(estado="justificativas"))
            )

        def finalizados(self):
            data = datetime.now()
            return super().get_queryset().filter(
                Q(mes=data.month - 1 if data.month != 1 else 12)
                & Q(ano=data.year if data.month != 1 else data.year - 1)
                & Q(estado='oficial')
            )

    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True)
    linhas = models.ManyToManyField(LinhaRelatorio, blank=True)
    estado = models.CharField(max_length=100, default="vazio")
    num_oficio = models.CharField(max_length=10)
    mes = models.IntegerField(
        default=mes_anterior(),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ]
    )
    ano = models.IntegerField(default=ano_padrao(), validators=[
                              MaxValueValidator(datetime.now().year)])
    data_fechamento = models.DateField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)
    vigentes = Vigente()

    def is_valid(self):
        return bool([linha for linha in self.linhas.all() if
                     linha.horas_extras > 0 or linha.adicional_noturno > 0 or linha.faltas > 0])

    @property
    def referencia(self):
        return str(self.mes) + "-" + str(self.ano)

    def __str__(self):
        try:
            return "%s - %d/%d" % (self.setor.nome, self.mes, self.ano)
        except:
            return "Setor excluído  ->  %d/%d" % (self.mes, self.ano)

    class Meta:
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"
        ordering = ['-criado_em', 'setor__nome']


class RelacaoAbono(models.Model):

    objects = models.Manager()
    abonos = models.ManyToManyField(Abono, blank=True)
    data_inicio = models.DateTimeField()
    data_termino = models.DateTimeField()

    class Meta:
        verbose_name = 'Relação de abonos'
        verbose_name_plural = "Relações de abonos"
        ordering = ['-data_inicio']

    @staticmethod
    def factory(data_inicio, data_termino):
        abonos = Abono.objects.filter(
            Q(deferido=True)
            & Q(criado_em__gte=data_inicio)
            & Q(criado_em__lte=data_termino)
        )
        relacao = RelacaoAbono.objects.create(
            data_inicio=data_inicio,
            data_termino=data_termino
        )
        print("\nRelação.abonos: %s\n" % relacao.abonos.all())
        print("\nAbonos: %s" % abonos)
        for abono in abonos.all():
            print("Abono: %s" % abono.__str__())
            try:
                relacao.abonos.add(abono)
            except Exception as bwe:
                print(bwe.details)

        relacao.save()
        return relacao


def valida_ferias(ferias):
    hoje = timezone.now().date()
    trabalhador = ferias.trabalhador
    inicio = ferias.data_inicio

    f = Ferias.objects.filter(Q(trabalhador=trabalhador) & (
        Q(data_inicio__range=(ferias.data_inicio, ferias.data_termino)) |
        Q(data_termino__range=(ferias.data_inicio, ferias.data_termino))) &
        Q(data_termino__gt=hoje) & Q(deferida=True) & Q(tipo='f'))
    l = LicencaPremio.objects.filter(Q(trabalhador=trabalhador) & (Q(data_inicio__range=(ferias.data_inicio, ferias.data_termino)) | Q(
        data_termino__range=(ferias.data_inicio, ferias.data_termino))) & Q(deferida=True))
    a = Abono.objects.filter(Q(trabalhador=trabalhador) & Q(
        data__range=(ferias.data_inicio, ferias.data_termino)) & Q(deferido=True))

    if ferias.tipo == 'f':
        f = f.exclude(id=ferias.id)
    elif ferias.tipo == 'l':
        l = l.exclude(id=ferias.id)

    if l or f or a or inicio < hoje or inicio.weekday() in [5, 6]:
        if len(f):
            ferias.observacoes = "férias, de %s à %s, convergem com a data marcada" % (
                f[0].data_inicio.strftime("%d/%m/%Y"), f[0].data_termino.strftime("%d/%m/%Y"))
        elif len(l):
            ferias.observacoes = "licença-prêmio de %s à %s, convergem com a data marcada" % (
                l[0].data_inicio.strftime("%d/%m/%Y"), l[0].data_termino.strftime("%d/%m/%Y"))
        elif len(a):
            ferias.observacoes = "abono em %s, converge com a data marcada" % (
                a[0].data.strftime("%d/%m/%Y"))
        elif inicio < hoje:
            ferias.observacoes = "data de agendamento Anterior a data do pedido"
            return True
        elif inicio.weekday() in [5, 6]:
            ferias.observacoes = "agendamento em fim de semana"

        return False

    return True


def valida_abono2(abono):
    try:
        valido = False
        data = timezone.now().date()
        pontuacao_abono = 1 if abono.expediente == 'integral' else 0.5
        f = Ferias.objects.filter(
            Q(tipo='f') &
            Q(deferida=True) &
            Q(trabalhador=abono.trabalhador) &
            Q(data_inicio__lte=abono.data) &
            Q(data_termino__gte=abono.data)
        )
        l = LicencaPremio.objects.filter(
            Q(deferida=True) &
            Q(trabalhador=abono.trabalhador) &
            Q(data_inicio__lte=abono.data) &
            Q(data_termino__gte=abono.data)
        )
        a = Abono.objects.filter(
            Q(trabalhador=abono.trabalhador) &
            Q(data=abono.data) &
            Q(deferido=True)
        )

        if len(a):
            abono.observacoes = "converger com outro abono em %s" % a[0].data.strftime(
                "%d/%m/%Y")
        elif len(f):
            abono.observacoes = "estar de férias no dia %d" % abono.data.day
        elif len(l):
            abono.observacoes = "estar de licença no dia %d" % abono.data.day
        elif contagem_abonos('ano', abono) >= 6:
            abono.observacoes = "não ter mais abonos restantes"
        elif contagem_abonos('mes', abono) + pontuacao_abono > 1:
            abono.observacoes = "já ter abonado ou ter marcado abono pra esse mês"
        elif data.day in [5, 6]:
            abono.observacoes = "ser final de semana"
        else:
            valido = True

        return valido

    except Exception:
        traceback.print_exc()


def contagem_abonos(tempo, abono):
    counter = 0.0
    if tempo == 'mes':
        abonos = Abono.objects.filter(
            Q(trabalhador=abono.trabalhador) &
            Q(deferido=True) &
            Q(data__year=timezone.now().year)
        )
    elif tempo == 'ano':
        abonos = Abono.objects.filter(
            Q(trabalhador=abono.trabalhador) &
            Q(deferido=True) &
            Q(data__year=timezone.now().year)
        )

    abonos = abonos.exclude(id=abono.id)

    print("abonos: %s" % abonos)
    for a in abonos:
        if (tempo == 'mes' and a.data.month == abono.data.month) or tempo == 'ano':
            if a.expediente == 'integral':
                counter += 1.0
            else:
                counter += .5
    print('contagem %s: %.1f' % (tempo, counter))

    return counter


class WorkerFactory:

    @staticmethod
    def create_random_workers(how_many):
        workers_data = WorkerFactory.random_worker_list(
            how_many, name_lenght=random.randint(2, 4))
        trabalhadores = []
        for data in workers_data:
            trabalhadores.append(
                Trabalhador.objects.create(
                    nome=data[0],
                    matricula=data[1],
                    funcao=data[2],
                    data_admissao=data[3],
                    situacao=data[4],
                )
            )
        return trabalhadores

    @staticmethod
    def random_worker_list(how_many, name_lenght=2):
        workers_list = []
        roles = [
            'Mecânico',
            'Tratorista',
            'Motorista',
            'Agente de Serviços',
            'Borracheiro',
            'Agente Administrativo',
        ]
        names = WorkerFactory.get_names(how_many, name_lenght)
        for name in names:
            random_role = random.randint(0, len(roles) - 1)
            random_matricula = str(random.randint(8000, 19999))
            random_date = WorkerFactory.get_random_date()
            worker = [name, random_matricula,
                      roles[random_role], random_date, 'ativo']
            workers_list.append(worker)

        return workers_list

    @staticmethod
    def get_names(how_many: int, name_length: int):
        if how_many > 0:
            with open('/kratos/python/feriapp/tests/name_list.txt', 'rb') as file:
                lines = file.readlines()
                names = []
                for each in range(how_many):
                    string = ''
                    for _ in range(name_length):
                        string += WorkerFactory.string_treatment(
                            lines[random.randint(0, len(lines))]) + ' '
                    string.strip()

                    names.append(string)

            return names
        else:
            raise Exception("%d <= 0!" & how_many)

        return name_list

    @staticmethod
    def string_treatment(string: str):
        return string.decode('utf-8').strip('\n')

    @staticmethod
    def get_random_date():
        dia = random.randint(1, 28)
        mes = random.randint(1, 12)
        ano = random.randint(1993, 2020)
        hora = '12:'
        minuto = '00'

        return str(ano) + '-' + (str(mes) if mes > 9 else '0' + str(mes)) + '-' + (
            str(dia) if dia > 9 else '0' + str(dia)) + " " + hora + minuto
