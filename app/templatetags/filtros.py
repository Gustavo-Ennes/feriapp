from django import template
from app.models import *
from app.forms import *
from datetime import datetime, timedelta
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
    ferias = Ferias.objects.filter(
        Q(data_inicio__gte=hoje) & Q(trabalhador=trabalhador) & Q(deferida=True) & Q(tipo='f'))
    licencas = LicencaPremio.objects.filter(Q(data_inicio__gte=hoje) & Q(trabalhador=trabalhador) & Q(deferida=True))
    if ferias:
        return ferias[0]
    if licencas:
        return licencas[0]


@register.filter
def folgas_acabando(trabalhador):
    hoje = datetime.today()
    ferias = Ferias.objects.filter(
        Q(data_inicio__lte=hoje) & Q(data_termino__gt=hoje) & Q(trabalhador=trabalhador) & Q(deferida=True) & Q(
            tipo='f'))
    licencas = LicencaPremio.objects.filter(
        Q(data_inicio__lte=hoje) & Q(data_termino__gt=hoje) & Q(trabalhador=trabalhador) & Q(deferida=True))
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
        form = TrabalhadorFormSemAdmissao(instance=obj)

    if tipo == "SetorForm":
        obj = Setor.objects.get(id=pk)
        form = SetorForm(instance=obj)

    return form


@register.filter
def qtd_servidores(setor):
    print(setor)
    return Trabalhador.objects.filter(setor=setor).count()


@register.filter
def verifica_tipo(obj, tipo):
    if type(obj) == Abono:
        return True
    elif tipo == "licenca":
        return obj.tipo == 'l'
    elif tipo == "ferias":
        return obj.tipo == 'f'


@register.filter
def inteiro(string):
    return int(string)


@register.filter
def soma_dias(data, dias):
    return (data + timedelta(days=dias)).strftime("%d/%m/%Y")


@register.filter
def subtrai_dias(data, dias):
    data = datetime.strptime(data, "%d/%m/%Y")
    return (data - timedelta(days=dias)).strftime("%d/%m/%Y")


@register.filter
def horas_justificadas(trabalhador):
    data = datetime.now()
    relatorio = None
    linha = None
    try:
        relatorio = Relatorio.objects.get(
            Q(setor=trabalhador.setor) & Q(criado_em__month=data.month) & Q(criado_em__year=data.year) & Q(
                estado='justificativas'))
        linha = relatorio.linhas.get(Q(trabalhador=trabalhador))
        print(relatorio, linha)
    except:
        print('Query de busca de relatório incorreta')
        return
    return str(linha.horas_extras).replace(',', '.') if linha else 0.0


@register.simple_tag
def mes_anterior():
    data = datetime.now()
    return data.month - 1 if data.month > 1 else 12


@register.simple_tag
def ano_padrao():
    data = datetime.now()
    return data.year - 1 if data.month == 1 else data.year


@register.filter
def mes_escrito(num):
    if num == 1:
        return 'janeiro'
    if num == 2:
        return 'fevereiro'
    if num == 3:
        return 'março'
    if num == 4:
        return 'abril'
    if num == 5:
        return 'maio'
    if num == 6:
        return 'junho'
    if num == 7:
        return 'julho'
    if num == 8:
        return 'agosto'
    if num == 9:
        return 'setembro'
    if num == 10:
        return 'outubro'
    if num == 11:
        return 'novembro'
    if num == 12:
        return 'dezembro'


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

