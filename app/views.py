from django.shortcuts import render, redirect
from app.models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
from app.forms import *
from app.tasks import atualiza_situacoes_trabalhadores
from django.views.generic import View
from .render import Render
from itertools import chain
import operator
from django.contrib.auth.mixins import LoginRequiredMixin
from .tasks import *


@login_required(login_url='/entrar/')
def index(request):
    context = {
        'FeriasForm' : FeriasForm(),
        'LicencaPremioForm' : LicencaPremioForm(),
        'AbonoForm' : AbonoForm(),
        'TrabalhadorForm' : TrabalhadorForm(),
        'SetorForm' : SetorForm(),
        'trabalhadores' : Trabalhador.objects.all(),
        'index' : True,
        'proximas_folgas': proximas_folgas(),
        'proximos_retornos' : proximos_retornos(),


    }

    atualiza_situacoes_trabalhadores()

    return render(request, 'index.html', context)

@login_required(login_url='/entrar/')
def ferias(request):
    hoje = timezone.now().date()
    context = {
        'futuras' : Ferias.objects.filter(Q(deferida=True) & Q(tipo='f') & Q(data_inicio__gt=hoje)),
        'fruidas' : Ferias.fruidas.all(),
        'indeferidas' : Ferias.indeferidas.all(),
        'em_andamento' : Ferias.em_andamento.all(),
        'tipo' : 'ferias',
        'FeriasForm' : FeriasForm(),
    }
    return render(request, 'ferias.html', context)

@login_required(login_url='/entrar/')
def licenca_premio(request):
    hoje = timezone.now().date()
    context = {
        'futuras' : LicencaPremio.objects.filter(Q(deferida=True) & Q(data_inicio__gt=hoje)),
        'fruidas' : LicencaPremio.fruidas.all(),
        'indeferidas' : LicencaPremio.indeferidas.all(),
        'em_andamento' : LicencaPremio.em_andamento.all(),
        'tipo' : 'licenca',
        'LicencaPremioForm' : LicencaPremioForm(),
    }
    return render(request, 'licenca.html', context)

@login_required(login_url='/entrar/')
def abono(request):
    hoje = timezone.now().date()
    context = {
            'futuros' : Abono.objects.filter(Q(deferido=True) & Q(data__gt=hoje)),
            'fruidos' : Abono.fruidos.all(),
            'indeferidos' : Abono.indeferidos.all(),
            'em_andamento' : Abono.em_andamento.all(),
            'tipo' : 'abono',
            'AbonoForm': AbonoForm(),
        }

    return render(request, 'abono.html', context)

@login_required(login_url='/entrar/')
def trabalhador(request):
    if request.method == "POST":
        id = int(request.POST['trabalhador'])
        hoje = timezone.now().date()
        try:
            trabalhador = Trabalhador.objects.get(id=id);
        except:
            messages.error(request, "Trabalhador não encontrado.")
            return redirect('index')
        finally:
            context = {
                'trabalhador' : trabalhador,
                'ferias_futuras' : Ferias.objects.filter(Q(trabalhador=trabalhador) & Q(deferida=True) & Q(tipo='f') & Q(data_inicio__gte=hoje)),
                'ferias_fruidas' : Ferias.fruidas.all().filter(Q(trabalhador=trabalhador)),
                'ferias_indeferidas' : Ferias.indeferidas.all().filter(Q(trabalhador=trabalhador)),
                'licencas_futuras' : LicencaPremio.objects.filter(Q(trabalhador=trabalhador) & Q(deferida=True) & Q(data_inicio__gte=hoje)),
                'licencas_fruidas' : LicencaPremio.fruidas.all().filter(Q(trabalhador=trabalhador)),
                'licencas_indeferidas' : LicencaPremio.indeferidas.all().filter(Q(trabalhador=trabalhador)),
                'abonos_futuros' : Abono.objects.filter(Q(trabalhador=trabalhador) & Q(deferido=True) & Q(data__gte=hoje)),
                'abonos_fruidos' : Abono.fruidos.all().filter(Q(trabalhador=trabalhador)),
                'abonos_indeferidos' : Abono.indeferidos.all().filter(Q(trabalhador=trabalhador)),
                'TrabalhadorForm' : TrabalhadorForm(),
            }
            print(context)
            return render(request, 'trabalhador.html', context)

@login_required(login_url='/entrar/')
def setor(request):
    setores = {}

    for setor in Setor.objects.all():
        setores[setor.nome]  = {
            'setor' : setor,
            'trabalhadores' : Trabalhador.objects.filter(setor=setor),
            'contagem' : Trabalhador.objects.filter(setor=setor).count(),
            'SetorForm' : SetorForm(),
        }


    context = {
        'setores' : setores,
        'SetorForm' : SetorForm(),
    }
    return render(request, 'setor.html', context)

@login_required(login_url='/entrar/')
def setor_espec(request):
    if request.method == "POST":
        setor = None
        try:
            setor = Setor.objects.get(id=int(request.POST['setor']))
        except:
            messages.error(request, "Não foi possível localizar tal setor.")
            return redirect('index')
        finally:
            context = {
                'setor' : setor,
                'trabalhadores' : Trabalhador.objects.filter(setor=setor),
            }
            return render(request, 'setor_espec.html', context)


@login_required(login_url='/entrar/')
def marcar_ferias(request):
    if request.method == "POST":
        form = FeriasForm(request.POST)
        if form.is_valid():
            obj = form.save()
            hoje = timzezone.now().date()
            if obj and obj.deferida and obj.data_inicio >= hoje:
                messages.success(request,'Você marcou férias para o servidor %s de %s à %s.' % (obj.trabalhador.nome, obj.data_inicio.strftime("%d/%d/%Y"), obj.data_termino.strftime("%d/%d/%Y")))
            else:
                messages.error(request, "O trabalhador não pode tirar férias nessa data por %s." % obj.observacoes)
        else:
            messages.error(request, form.errors)

        return redirect("ferias")


@login_required(login_url='/entrar/')
def marcar_licenca(request):
    if request.method == "POST":
        form = LicencaPremioForm(request.POST)
        if form.is_valid():
            hoje = timzeone.now().date()
            obj = form.save()
            if obj and obj.deferida and obj.data_inicio >= hoje:
                messages.success(request,'Você marcou licença-prêmio para o servidor %s de %s à %s.' % (obj.trabalhador.nome, obj.data_inicio.strftime("%d/%d/%Y"), obj.data_termino.strftime("%d/%d/%Y")))
            else:
                messages.error(request, "O trabalhador não pode tirar licença-prêmio nessa data por %s." % obj.observacoes)
        else:
            messages.error(request, form.errors)

        return redirect("licenca_premio")


@login_required(login_url='/entrar/')
def marcar_abono(request):
    if request.method == "POST":
        form = AbonoForm(request.POST)
        if form.is_valid():
            hoje = timzeone.now().date()
            obj = form.save()
            if obj and obj.deferido and obj.data >= hoje:
                messages.success(request,'Você marcou um abono para o servidor %s em %s.' % (obj.trabalhador.nome, obj.data.strftime("%d/%d/%Y")))
            else:
                messages.error(request, "O trabalhador não pode abonar nessa data por %s." % obj.observacoes)
        else:
            messages.error(request, form.errors)

        return redirect("abono")


@login_required(login_url='/entrar/')
def novo_setor(request):
    if request.method == "POST":
        form = SetorForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request,'Você cadastrou um novo setor: %s.' % (obj.nome))
        else:
            messages.error(request, form.errors)

        return redirect("setor")


@login_required(login_url='/entrar/')
def novo_trabalhador(request):
    if request.method == "POST":
        form = TrabalhadorForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request,'Você cadastrou um novo trabalhador: %s - %s .' % (obj.nome, obj.funcao))
        else:
            messages.error(request, form.errors)

        return redirect("trabalhadores")

@login_required(login_url='/entrar/')
def  trabalhadores(request):
    trabalhadores = Trabalhador.objects.all()
    context = {
        'trabalhadores' : trabalhadores,
        'TrabalhadorForm' : TrabalhadorForm(),
    }
    return render(request, 'trabalhadores.html', context)


@login_required(login_url='/entrar/')
def pesquisa(request):
    if request.method == "POST":
        hoje = timezone.now().date()
        query = request.POST['query']
        context =  {
            'ferias_futuras' : Ferias.objects.filter(
                (
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ) &
                Q(deferida=True) &
                Q(data_termino__gte=hoje) &
                Q(tipo='f')
            ),
            'ferias_fruidas' : Ferias.fruidas.filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)
            ),
            'ferias_indeferidas' : Ferias.indeferidas.filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)

            ),
            'licencas_futuras' : LicencaPremio.objects.filter(
                (
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ) &
                Q(deferida=True) &
                Q(data_termino__gte=hoje)
            ),
            'licencas_fruidas' : LicencaPremio.fruidas.filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)
            ),
            'licencas_indeferidas' : LicencaPremio.indeferidas.filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)
            ),
            'abonos_futuros' : Abono.objects.filter(
                (
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ) &
                Q(deferido=True) &
                Q(data__gte=hoje)
            ),
            'abonos_fruidos' : Abono.fruidos.filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)
            ),
            'abonos_indeferidos' : Abono.indeferidos.filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)
            ),
            'trabalhadores' : Trabalhador.objects.filter(
                Q(nome__icontains=query) |
                Q(funcao__icontains=query) |
                Q(setor__nome__icontains=query)
            ),
            'setores' : Setor.objects.filter(Q(nome__icontains=query)),
            'query' : query,
        }
        context['qtd_resultados'] = len(context['licencas_futuras']) + len(context['licencas_fruidas']) + len(context['licencas_indeferidas']) + len(context['abonos_fruidos']) + len(context['abonos_futuros']) + len(context['abonos_indeferidos']) + len(context['ferias_fruidas']) + len(context['ferias_futuras']) + len(context['ferias_indeferidas']) + len(context['trabalhadores']) + len(context['setores'])

        return render(request, 'pesquisa.html', context)


@login_required(login_url='/entrar/')
def editar_data(request):
    if request.method == "POST":
        verbose_name = ""
        obj = None
        return_name = ""

        tipo = request.POST['tipo']
        pk = int(request.POST['id'])
        data = request.POST['data']

        if tipo == 'licenca':

            obj = LicencaPremio.objects.get(id=pk)
            verbose_name = "licença-prêmio"
            obj.data_inicio = datetime.strptime(data, '%d/%m/%Y')
            obj.data_termino = obj.data_inicio + timedelta(days=obj.qtd_dias - 1)
            obj.save()
            return_name = "licenca_premio"

        elif tipo == 'abono':

            obj = Abono.objects.get(id=pk)
            verbose_name = tipo
            obj.data = datetime.strptime(data, '%d/%m/%Y')
            obj.save()
            return_name = "abono"

        elif tipo == 'ferias':

            obj = Ferias.objects.get(id=pk)
            verbose_name = tipo
            obj.data_inicio = datetime.strptime(data, '%d/%m/%Y')
            obj.data_termino = obj.data_inicio + timedelta(days=obj.qtd_dias - 1)
            obj.save()
            return_name = "ferias"

        messages.success(request, "Você editou a data do(a) %s do servidor %s para %s." % (verbose_name, obj.trabalhador.nome, data))

        return redirect(return_name)

@login_required(login_url='/entrar/')
def editar_trabalhador(request):
    if request.method == "POST":
        trabalhador = Trabalhador.objects.get(id=int(request.POST['id']))
        form = TrabalhadorForm(request.POST, instance=trabalhador)
        obj = form.save()
        messages.success(request, "Você editou os dados de %s." % (trabalhador.nome))
        return redirect("trabalhadores")


@login_required(login_url='/entrar/')
def editar_setor(request):
    if request.method == "POST":
        setor = Setor.objects.get(id=int(request.POST['id']))
        form = SetorForm(request.POST, instance=setor)
        obj = form.save()
        messages.success(request, "Você editou o setor %s." % (setor.nome))
        return redirect("setor")

@login_required(login_url='/entrar/')
def excluir_setor(request):
    if request.method == "POST":
        setor = Setor.objects.get(id=int(request.POST['setor_id']))
        messages.success(request, "Você deletou o setor %s." % ( setor.nome ) )
        setor.delete()
        return redirect("setor")

@login_required(login_url='/entrar/')
def excluir_trabalhador(request):
    if request.method == "POST":
        trabalhador = Trabalhador.objects.get(id=int(request.POST['trabalhador_id']))
        messages.success(request, "Você excluir o servidor %s." % ( trabalhador.nome ) )
        trabalhador.delete()
        return redirect("trabalhadores")


class Pdf(LoginRequiredMixin, View):

    login_url = '/index/'
    redirect_field_name ="index"

    def post(self, request):
        tipo = request.POST['tipo']
        query = None
        today = timezone.now()
        hoje = today.date()

        if 'query' in request.POST:
            query = request.POST['query']

        if not query:
            context = {
                'pdf' : True,
                'today' : today,
                'trabalhadores' : Trabalhador.objects.all(),
                'setores' : Setor.objects.all(),
                'ferias_futuras' : Ferias.objects.filter(Q(deferida=True) & Q(tipo='f') & Q(data_termino__gte=hoje)),
                'ferias_fruidas' : Ferias.fruidas.all(),
                'ferias_indeferidas' :  Ferias.indeferidas.all(),
                'abonos_futuros' : Abono.objects.filter(Q(deferido=True) & Q(data__gte=hoje)),
                'abonos_fruidos' : Abono.fruidos.all(),
                'abonos_indeferidos' : Abono.indeferidos.all(),
                'licencas_futuras' : LicencaPremio.objects.filter(Q(deferida=True) & Q(data_termino__gte=hoje)),
                'licencas_fruidas' : LicencaPremio.fruidas.all(),
                'licencas_indeferidas' : LicencaPremio.indeferidas.all(),
                'tipo' : tipo,
                'user' : request.user
            }
        else:
            context =  {
                'ferias_futuras' : Ferias.objects.filter(
                    (
                        Q(trabalhador__nome__icontains=query) |
                        Q(trabalhador__funcao__icontains=query) |
                        Q(trabalhador__setor__nome__icontains=query)
                    ) &
                    Q(deferida=True) &
                    Q(data_termino__gte=hoje) &
                    Q(tipo='f')
                ),
                'ferias_fruidas' : Ferias.fruidas.filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ),
                'ferias_indeferidas' : Ferias.indeferidas.filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)

                ),
                'licencas_futuras' : LicencaPremio.objects.filter(
                    (
                        Q(trabalhador__nome__icontains=query) |
                        Q(trabalhador__funcao__icontains=query) |
                        Q(trabalhador__setor__nome__icontains=query)
                    ) &
                    Q(deferida=True) &
                    Q(data_termino__gte=hoje)
                ),
                'licencas_fruidas' : LicencaPremio.fruidas.filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ),
                'licencas_indeferidas' : LicencaPremio.indeferidas.filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ),
                'abonos_futuros' : Abono.objects.filter(
                    (
                        Q(trabalhador__nome__icontains=query) |
                        Q(trabalhador__funcao__icontains=query) |
                        Q(trabalhador__setor__nome__icontains=query)
                    ) &
                    Q(deferido=True) &
                    Q(data__gte=hoje)
                ),
                'abonos_fruidos' : Abono.fruidos.filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ),
                'abonos_indeferidos' : Abono.indeferidos.filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ),
                'trabalhadores' : Trabalhador.objects.filter(
                    Q(nome__icontains=query) |
                    Q(funcao__icontains=query) |
                    Q(setor__nome__icontains=query)
                ),
                'setores' : Setor.objects.filter(Q(nome__icontains=query)),
                'query' : query,
                'tipo' : tipo,
                'pdf' : True,
                'today' : today,
                'user' : request.user
            }
        print(context)
        return Render.render('pdf.html', context)

@login_required(login_url='/entrar/')
def indeferir(request):

    if request.method == "POST":
        obj = None
        pk = None
        tipo = request.POST['tipo']
        voltar_para = ""
        mensagem = tipo.title() + " indeferida(o). Motivo:\n"
        mensagem += request.POST['observacoes']

        if tipo == "abono":
            pk = int(request.POST['abono_id'])
            obj = Abono.objects.get(id=pk)
            obj.deferido = False
            voltar_para = "abono"


        if tipo == "ferias":
            pk = int(request.POST['ferias_id'])
            obj = Ferias.objects.get(id=pk)
            obj.deferida = False
            voltar_para = "ferias"


        if tipo == "licenca":
            pk = int(request.POST['licenca_id'])
            obj = LicencaPremio.objects.get(id=pk)
            obj.deferida = False
            voltar_para = "licenca_premio"

        obj.observacoes = mensagem
        obj.save()
        messages.success(request, mensagem)

        return redirect(voltar_para)

def entrar(request):
    if request.method == "GET":
        context = {
            'LoginForm' : LoginForm(),
        }
        return render(request, 'login.html', context)

    elif request.method == "POST":
        logout(request)
        print(str(request.POST))
        username = request.POST['usuario']
        password = request.POST['senha']
        remember_me = True if 'remember_me' in request.POST else False

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                messages.success(request, 'Bem-vindo(a), %s' % user.username)

                return redirect("index")

            else:
                print("usuário não ativo.")

        else:
            messages.error(request, "Usuário ou senha inválida.")

        return redirect("entrar")


@login_required(login_url='/entrar/')
def sair(request):
    logout(request)
    return redirect("entrar")







def proximas_folgas():
    hoje = timezone.now().date()
    folgas = []
    limite_dias = 7

    #como o  tipo 'f' não foi especificado, e por LicencaPremio ser subclasse de Ferias, os dois tipos serão listados na próxima linha
    folgas = Ferias.objects.filter( Q(deferida=True) & Q(data_inicio__gte=hoje) & Q(data_inicio__lt=hoje+timedelta(days=limite_dias)))
    abonos = Abono.objects.filter(Q(deferido=True) & Q(data__gt=hoje) & Q(data__lt=hoje + timedelta(days=limite_dias)))
    folgas = list(chain(abonos, folgas))

    folgas = sorted( folgas , key=lambda obj: obj.data_inicio if "data_inicio" in dir(obj) else obj.data)

    print('folgar', folgas)

    return folgas

def proximos_retornos():
    hoje = timezone.now().date()
    folgas = []
    limite_dias = 7

    #como o  tipo 'f' não foi especificado, e por LicencaPremio ser subclasse de Ferias, os dois tipos serão listados na próxima linha
    folgas = Ferias.objects.filter( Q(deferida=True) & Q(data_termino__gt=hoje) & Q(data_termino__lte=hoje+timedelta(days=limite_dias)))
    abonos = Abono.objects.filter(Q(deferido=True) & Q(data=hoje))
    folgas = list(chain(abonos, folgas))

    print('antes do sort', folgas)
    folgas = sorted( folgas, key=lambda obj: obj.data_inicio if "data_inicio" in dir(obj) else obj.data)
    print('retornos', folgas)

    return folgas
