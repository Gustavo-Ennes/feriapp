from django import template
from app.models import *
from app.forms import *
from datetime import datetime
from django.db.models import Q

register = template.Library()

@register.filter
def dias_ate(data):
    hoje = datetime.today()
    dias = data - hoje.date()
    return dias.days

@register.filter
def menos_que_sete(num):
    return num <= 7

@register.filter
def futuras_folgas(trabalhador):
    hoje = datetime.today()
    ferias = Ferias.objects.filter(Q(data_inicio__gte=hoje) & Q(trabalhador=trabalhador) & Q(deferida=True))
    licencas = LicencaPremio.objects.filter(Q(data_inicio__gte=hoje) & Q(trabalhador=trabalhador) & Q(deferida=True))
    if ferias:
        return ferias[0]
    if licencas:
        return licencas[0]


@register.filter
def folgas_acabando(trabalhador):
    hoje = datetime.today()
    ferias = Ferias.objects.filter(Q(data_inicio__lte=hoje) & Q(data_termino__gt=hoje) & Q(trabalhador=trabalhador) & Q(deferida=True))
    licencas = LicencaPremio.objects.filter(Q(data_inicio__lte=hoje) & Q(data_termino__gt=hoje) & Q(trabalhador=trabalhador) & Q(deferida=True))
    if ferias:
        return ferias[0]
    if licencas:
        return licencas[0]


@register.filter
def formulario_preenchido(tipo, pk):
    obj = None
    form = None
    if tipo == "AbonoForm":
        obj = Abono.objects.get(id=pk)
        form = AbonoForm(instance=obj)

    if tipo == "TrabalhadorForm":
        obj = Trabalhador.objects.get(id=pk)
        form = TrabalhadorForm(instance=obj)

    if tipo == "SetorForm":
        obj = Setor.objects.get(id=pk)
        form = SetorForm(instance=obj)

    return form

@register.filter
def qtd_servidores(setor):
    return Trabalhador.objects.filter(setor=setor).count()


@register.filter
def verifica_tipo(obj, tipo):
    if tipo == "abono":
        return type(obj) == Abono
    if tipo == "licenca":
        return type(obj) == LicencaPremio
    if tipo == "ferias":
        return type(obj) == Ferias