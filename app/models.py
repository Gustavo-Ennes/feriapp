from django.db import models
from datetime import datetime, timedelta
from django.contrib import messages
from django.db.models import  Q
from django.utils import timezone
# Create your models here.




class Setor(models.Model):
    nome = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s - desde %s' % (self.nome, self.criado_em.strftime("%d/%m/%Y"))


    class Meta:
        verbose_name_plural = 'Setores'
        ordering = ['nome']

class Trabalhador(models.Model):
    OPCOES = (
        ('ferias', "Férias"),
        ('licenca', "Licença-prêmio"),
        ('abono', "Abono"),
        ('ativo', "Ativo"),
        ('atestado', "Atestado Médico"),
    )

    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=15)
    funcao = models.CharField(max_length=50)
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True)
    data_admissao = models.DateTimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)
    situacao = models.CharField(max_length=100, choices=OPCOES)


    def __str__(self):
        return '%s : %s - %s - desde %s' % (self.nome, self.funcao, self.setor.nome, self.criado_em.strftime("%d/%m/%Y"))

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
            return super().get_queryset().filter(Q(tipo='f') & Q(data_termino__lt=timezone.now().date()) & Q(deferida=True))
            #return Ferias.objects.filter(Q(tipo='f') & Q(data_termino__lt=timezone.now().date()) & Q(deferida=True))
    class FeriasIndeferidas(models.Manager):
        def all(self):
            return super().get_queryset().filter(Q(deferida=False))

            #return Ferias.objects.filter(Q(deferida=False))
    class FeriasEmAndamento(models.Manager):
        def all(self):
            return super().get_queryset().filter(Q(tipo='f') & Q(data_inicio__lte=timezone.now().date()) & Q(data_termino__gte=timezone.now().date()) & Q(deferida=True))
            #return Ferias.objects.filter(Q(tipo='f') & Q(deferida=True) & Q(data_inicio__lte=timezone.now().date()) & Q(data_termino__gte=timezone.now().date()))

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


    def save(self, *args, **kwargs):

        self.data_termino = self.data_inicio + timedelta(days=self.qtd_dias)
        self.deferida = valida_ferias(self)
        super(Ferias, self).save(*args, **kwargs)


    def __str__(self):
        return '%d dias - %s -saindo %s' % (self.qtd_dias,self.trabalhador.nome, self.data_inicio.strftime("%d/%m/%Y"))

    class Meta:
        verbose_name_plural = "Férias"
        verbose_name = "Férias"
        ordering = ['data_inicio']

class LicencaPremio(Ferias):

    objects = models.Manager()

    class LicencasFruidas(models.Manager):
        def all(self):
            return super().get_queryset().filter(Q(data_termino__lt=timezone.now().date()) & Q(deferida=True))
            #return LicencaPremio.objects.filter(Q(data_termino__lt=timezone.now().date()) & Q(deferida=True))
    class LicencasIndeferidas(models.Manager):
        def all(self):
            return super().get_queryset().filter(Q(deferida=False))
            #return LicencaPremio.objects.filter(Q(deferida=False))
    class LicencaEmAndamento(models.Manager):
        def all(self):
            return super().get_queryset().filter(Q(data_inicio__lte=timezone.now().date()) & Q(deferida=True) & Q(data_termino__gte=timezone.now().date()))

            #return LicencaPremio.objects.filter(Q(deferida=True) & Q(data_inicio__lte=timezone.now().date()) & Q(data_termino__gte=timezone.now().date()))

    fruidas = LicencasFruidas()
    indeferidas = LicencasIndeferidas()
    em_andamento = LicencaEmAndamento()

    def __str__(self):
        return '%d dias - %s -saindo %s' % (self.qtd_dias, self.trabalhador.nome, self.data_inicio.strftime("%d/%m/%Y"))

    def save(self, *args, **kwargs):

        self.data_termino = self.data_inicio + timedelta(days=self.qtd_dias)
        self.tipo = 'l'
        valida_ferias(self)
        super(LicencaPremio, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Licença Prêmio"
        verbose_name = "Licenças Prêmio"
        ordering = ['data_inicio']

class Abono(models.Model):


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
    data = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)
    deferido = models.BooleanField(editable=False, default=False)
    observacoes = models.TextField(blank=True, editable=False)
    fruido = models.BooleanField(editable=False, default=False)

    def save(self, *args, **kwargs):

        self.deferido = valida_abono(self)
        super(Abono, self).save(*args, **kwargs)

    def __str__(self):
        return '%s - %s' % (self.trabalhador.nome, self.data.strftime("%d/%m/%Y"))

    class Meta:
        ordering = ['data']



def valida_ferias(ferias):
    hoje = timezone.now().date()
    trabalhador = ferias.trabalhador
    inicio = ferias.data_inicio

    f = Ferias.objects.filter(Q(trabalhador=trabalhador) & ( Q(data_inicio__range=(ferias.data_inicio, ferias.data_termino)) | Q(data_termino__range=(ferias.data_inicio, ferias.data_termino))) & Q(data_termino__gt=hoje) & Q(deferida=True) & Q(tipo='f'))
    l = LicencaPremio.objects.filter(Q(trabalhador=trabalhador) & ( Q(data_inicio__range=(ferias.data_inicio, ferias.data_termino)) | Q(data_termino__range=(ferias.data_inicio, ferias.data_termino))) & Q(deferida=True))
    a = Abono.objects.filter(Q(trabalhador=trabalhador) & Q(data__range=(ferias.data_inicio, ferias.data_termino)) & Q(deferido=True))
    '''
    if f or l or a:
        return False
    '''
    if l or f or a or inicio < hoje or ferias.observacoes:
        if ferias.observacoes:
            pass
        if len(f):
            ferias.observacoes = "férias, de %s à %s, convergem com a data marcada" % ( f[0].data_inicio.strftime("%d/%m/%Y"),f[0].data_termino.strftime("%d/%m/%Y"))
        elif len(l):
            ferias.observacoes = "licença-prêmio de %s à %s, convergem com a data marcada" % ( l[0].data_inicio.strftime("%d/%m/%Y"),l[0].data_termino.strftime("%d/%m/%Y"))
        elif len(a):
            ferias.observacoes = "abono em %s, converge com a data marcada" % (a[0].data.strftime("%d/%m/%Y"))
        elif inicio < hoje:
            ferias.observacoes = "data de agendamento anterior a hoje"
            ferias.fruida = True
            return True

        return False

    return True

def valida_abono(abono):

    hoje = timezone.now().date()
    trabalhador = abono.trabalhador
    data = abono.data

    f = Ferias.objects.filter(Q(trabalhador=trabalhador) &  Q(data_inicio__lte=data) & Q(data_termino__gt=data) & Q(deferida=True) & Q(tipo='f'))
    l = LicencaPremio.objects.filter(Q(trabalhador=trabalhador) &  Q(data_inicio__lte=data) & Q(data_termino__gt=data) & Q(deferida=True))
    a = Abono.objects.filter(Q(trabalhador=trabalhador) & Q(data__year=abono.data.year) & Q(data__month=abono.data.month) & Q(data__day=abono.data.day) & Q(deferido=True))


    if l or f or a or data < hoje or abono.observacoes:
        if abono.observacoes:
            pass
        elif len(f):
            abono.observacoes = "férias, de %s à %s, convergem com a data marcada" % (f[0].data_inicio.strftime("%d/%m/%Y"),f[0].data_termino.strftime("%d/%m/%Y"))
        elif len(l):
            abono.observacoes = "licença-prêmio de %s à %s, convergem com a data marcada" % ( l[0].data_inicio.strftime("%d/%m/%Y"),l[0].data_termino.strftime("%d/%m/%Y"))
        elif len(a):
            abono.observacoes = "abono em %s, converge com a data marcada" % (a[0].data.strftime("%d/%m/%Y"))
        elif data < hoje:
            abono.observacoes = "data de agendamento anterior a hoje"
            abono.fruido = True
            return True

        return False

    return True
