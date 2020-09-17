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
    return data + timedelta(days=dias)

@register.filter
def check_amanha(data):
    print('data:', data, ' ~ amanhã:', datetime.now().date() + timedelta(days=1))
    if data == datetime.now().date():
        return "Hoje"
    elif data == datetime.now().date() + timedelta(days=1):
        return "Amanhã"
    return data.strftime("%d/%m/%Y")


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


@register.simple_tag
def data():
    data = datetime.now()
    s = dia_escrito(data.weekday()) + ", "
    s += str(data.day) + " de " + mes_escrito(data.month).title() + " de " + str(data.year)
    return s


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


@register.filter
def dia_escrito(dia):
    if dia == 0:
        return "Segunda-Feira"
    elif dia == 1:
        return "Terça-Feira"
    elif dia == 2:
        return "Quarta-Feira"
    elif dia == 3:
        return "Quinta-Feira"
    elif dia == 4:
        return "Sexta-Feira"
    elif dia == 5:
        return 'Sábado'
    elif dia == 6:
        return "Domingo"


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter
def num_oficio_do_setor(setor):
    return Relatorio.vigentes.em_aberto().get(setor=setor).num_oficio


@register.filter
def trabalhador_por_usuario(usuario):
    try:
        return Trabalhador.objects.get(Q(user=usuario))
    except Exception as e:
        print("Trabalhador não encontrado:", e)
        return None


@register.filter
def trabalhador_por_id(id):
    if id:
        try:
            return Trabalhador.objects.get(id=int(id))
        except Exception as e:
            print(e)


@register.filter
def atestado_com_trabalhador(trabalhador):
    f = AtestadoForm()
    f.fields['trabalhador'].queryset = Trabalhador.objects.filter(Q(id=trabalhador.id))
    f.fields['trabalhador'].empty_label = None
    return f


@register.filter
def referencia(linhaRelatorio):
    try:
        r = Relatorio.objects.get(Q(linha=linhaRelatorio))
    except Exception as e:
        print(e)
    return "{r.mes}/{r.ano}" if r else None


@register.filter 
def get_referencias(relatorios):
    refs = []
    for r in relatorios:
        if not r.referencia in refs:
            refs.append(r.referencia)
    return refs

