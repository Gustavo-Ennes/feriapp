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
        'em_andamento' : em_andamento(),
        'AutorizacaoForm' : AutorizacaoForm(),


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
            hoje = timezone.now().date()
            if obj and obj.deferida and obj.data_inicio >= hoje:
                messages.success(request,'Você marcou férias para o servidor %s de %s à %s.' % (obj.trabalhador.nome, obj.data_inicio.strftime("%d/%d/%Y"), obj.data_termino.strftime("%d/%d/%Y")))
            else:
                messages.error(request, "O trabalhador não pode tirar férias nessa data por %s." % obj.observacoes)
        else:
            messages.error(request, form.errors)

        return redirect('ferias_pdf', ferias_id=obj.id) if obj.deferida else redirect('ferias')


@login_required(login_url='/entrar/')
def marcar_licenca(request):
    if request.method == "POST":
        form = LicencaPremioForm(request.POST)
        if form.is_valid():
            hoje = timezone.now().date()
            obj = form.save()
            if obj and obj.deferida and obj.data_inicio >= hoje:
                messages.success(request,'Você marcou licença-prêmio para o servidor %s de %s à %s.' % (obj.trabalhador.nome, obj.data_inicio.strftime("%d/%d/%Y"), obj.data_termino.strftime("%d/%d/%Y")))
            else:
                messages.error(request, "O trabalhador não pode tirar licença-prêmio nessa data por %s." % obj.observacoes)
        else:
            messages.error(request, form.errors)

        return redirect('licenca_pdf', licenca_id=obj.id) if obj.deferida else redirect("licenca_premio")


@login_required(login_url='/entrar/')
def marcar_abono(request):
    if request.method == "POST":
        form = AbonoForm(request.POST)
        if form.is_valid():
            hoje = timezone.now().date()
            obj = form.save()
            if obj and obj.deferido and obj.data >= hoje:
                messages.success(request,'Você marcou um abono para o servidor %s em %s.' % (obj.trabalhador.nome, obj.data.strftime("%d/%d/%Y")))
            else:
                messages.error(request, "O trabalhador não pode abonar nessa data por %s." % obj.observacoes)
        else:
            messages.error(request, form.errors)

        return redirect('abono_pdf', abono_id=obj.id) if obj.deferido else redirect("abono")


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
            'ferias_fruidas' : Ferias.fruidas.all().filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)
            ),
            'ferias_indeferidas' : Ferias.indeferidas.all().filter(
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
            'licencas_fruidas' : LicencaPremio.fruidas.all().filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)
            ),
            'licencas_indeferidas' : LicencaPremio.indeferidas.all().filter(
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
            'abonos_fruidos' : Abono.fruidos.all().filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)
            ),
            'abonos_indeferidos' : Abono.indeferidos.all().filter(
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
        data_antiga = None

        if tipo == 'licenca':

            obj = LicencaPremio.objects.get(id=pk)
            verbose_name = "licença-prêmio"
            data_antiga = obj.data_inicio
            obj.data_inicio = datetime.strptime(data, '%d/%m/%Y').date()
            obj.data_termino = obj.data_inicio + timedelta(days=obj.qtd_dias - 1)
            obj.save()
            return_name = "licenca_premio"

        elif tipo == 'abono':

            obj = Abono.objects.get(id=pk)
            verbose_name = tipo
            data_antiga = obj.data
            obj.data = datetime.strptime(data, '%d/%m/%Y').date()
            obj.save()
            return_name = "abono"

        elif tipo == 'ferias':

            obj = Ferias.objects.get(id=pk)
            verbose_name = tipo
            data_antiga = obj.data_inicio
            obj.data_inicio = datetime.strptime(data, '%d/%m/%Y').date()
            obj.data_termino = obj.data_inicio + timedelta(days=obj.qtd_dias - 1)
            obj.save()
            return_name = "ferias"

        if tipo == 'abono':
            if obj.deferido:
                messages.success(request, "Você editou a data do(a) %s do servidor %s para %s." % (verbose_name, obj.trabalhador.nome, data))
                obj.observacoes = "reagendado"
            else:
                obj.data = data_antiga
                messages.error(request, "O abono não pode ser editado por %s. A data original (%s) foi mantida" % ( obj.observacoes, obj.data.strftime("%d/%m/%Y")))
        elif tipo == ("ferias" or 'licenca'):
            if obj.deferida:
                messages.success(request, "Você editou a data do(a) %s do servidor %s para %s." % (verbose_name, obj.trabalhador.nome, data))
                obj.observacoes = "reagendada"
            else:
                obj.data_inicio = data_antiga
                obj.data_termino = obj.data_inicio + timedelta(days=obj.qtd_dias - 1)
                messages.error(request, "O(a) %s não pode ser editado por %s. A data original (%s) foi mantida" % ( verbose_name, obj.observacoes, obj.data_inicio.strftime("%d/%m/%Y")))

        obj.save()


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

    login_url = '/entrar/'
    redirect_field_name ="index"

    def post(self, request):
        tipo = request.POST['tipo']
        query = None
        today = timezone.now()
        hoje = today.date()

        if 'query' in request.POST:
            query = request.POST['query']

        if tipo == 'trabalhador_historico':
            try:
                trabalhador = Trabalhador.objects.get(id=int(request.POST['trabalhador_id']))
            except:
                messages.error(request, "Não existe trabalhador  com o id %d" % int(request.POST['trabalhador_id']))
                return redirect('trabalhadores')

            context = {
                'pdf' : True,
                'ferias_futuras' : Ferias.objects.filter(Q(trabalhador=trabalhador) & Q(deferida=True) & Q(tipo='f') & Q(data_inicio__gt=hoje)),
                'ferias_fruidas' : Ferias.fruidas.all().filter(Q(trabalhador=trabalhador)),
                'ferias_indeferidas' :  Ferias.indeferidas.all().filter(Q(trabalhador=trabalhador)),
                'abonos_futuros' : Abono.objects.filter(Q(trabalhador=trabalhador) & Q(deferido=True) & Q(data__gte=hoje)),
                'abonos_fruidos' : Abono.fruidos.all().filter(Q(trabalhador=trabalhador)),
                'abonos_indeferidos' : Abono.indeferidos.all().filter(Q(trabalhador=trabalhador)),
                'licencas_futuras' : LicencaPremio.objects.filter(Q(trabalhador=trabalhador) & Q(deferida=True) & Q(data_inicio__gt=hoje)),
                'licencas_fruidas' : LicencaPremio.fruidas.all().filter(Q(trabalhador=trabalhador)),
                'licencas_indeferidas' : LicencaPremio.indeferidas.all().filter(Q(trabalhador=trabalhador)),
                'tipo' : tipo,
                'trabalhador' : trabalhador,

            }

        elif tipo == "setor_historico":
            try:
                setor = Setor.objects.get(id=int(request.POST['setor_id']))
            except:
                messages.error(request,"Não há setor com id  %d" % int(request.POST['setor_id']))
                return redirect('setor')


            context = {
                'trabalhadores' : Trabalhador.objects.filter(Q(setor=setor)),
                'tipo' : request.POST['tipo'],
                'pdf' : True,
                'setor': setor
            }


        elif query:
            context =  {
                'ferias_futuras' : Ferias.objects.filter(
                    (
                        Q(trabalhador__nome__icontains=query) |
                        Q(trabalhador__funcao__icontains=query) |
                        Q(trabalhador__setor__nome__icontains=query)
                    ) &
                    Q(deferida=True) &
                    Q(data_inicio__gt=hoje) &
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
                    Q(data_inicio__gt=hoje)
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
                    Q(data__gt=hoje)
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

        else:
            context = {
                'pdf' : True,
                'today' : today,
                'trabalhadores' : Trabalhador.objects.all(),
                'setores' : Setor.objects.all(),
                'ferias_futuras' : Ferias.objects.filter(Q(deferida=True) & Q(tipo='f') & Q(data_inicio__gt=hoje)),
                'ferias_fruidas' : Ferias.fruidas.all(),
                'ferias_indeferidas' :  Ferias.indeferidas.all(),
                'abonos_futuros' : Abono.objects.filter(Q(deferido=True) & Q(data__gte=hoje)),
                'abonos_fruidos' : Abono.fruidos.all(),
                'abonos_indeferidos' : Abono.indeferidos.all(),
                'licencas_futuras' : LicencaPremio.objects.filter(Q(deferida=True) & Q(data_termino__gt=hoje)),
                'licencas_fruidas' : LicencaPremio.fruidas.all(),
                'licencas_indeferidas' : LicencaPremio.indeferidas.all(),
                'tipo' : tipo,
                'user' : request.user
            }

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


class AbonoPDF(LoginRequiredMixin, View):

    login_url = '/entrar/'
    redirect_field_name ="index"

    def get(self, request, abono_id):
        try:
            abono = Abono.objects.get(id=abono_id)
        except:
            messages.error(request,"Não há abono com id %d" % abono_id)
            return redirect('abono')

        if not abono.deferido:
            messages.error(request, "O abono(id=%d) solicitado foi deferido e não pode ser impresso" % abono_id)
            return redirect('abono')

        elif abono.fruido:
            messages.error(request, "O abono(id=%d) já foi fruido" % abono_id)
            return redirect('abono')

        else:

            hoje = timezone.now().date()

            context = {
                'data' : abono.data.strftime("%d/%m/%Y"),
                'dia_hj' : hoje.day,
                'mes_hj' : mes_escrito(hoje.month),
                'ano_hj' : hoje.year,
                'nome' : abono.trabalhador.nome,
                'matricula' : abono.trabalhador.matricula,
                'funcao' : abono.trabalhador.funcao,
                'setor' : abono.trabalhador.setor.nome

            }
            return Render.render('template_abono.html', context)


class FeriasPDF(LoginRequiredMixin, View):

    login_url = '/entrar/'
    redirect_field_name ="index"

    def get(self, request, ferias_id):
        try:
            ferias = Ferias.objects.get(id=ferias_id)
        except:
            messages.error(request, "Não há férias com id %d" % ferias_id)
            return redirect('ferias')

        if not ferias.deferida:
            messages.error(request, "A férias(id=%d) solicitada foi deferida e não pode ser impressa" % ferias_id)
            return redirect('ferias')

        elif ferias.fruida:
            messages.error(request, "A férias(id=%d) já foi fruida" % ferias_id)
            return redirect('ferias')

        else:

            hoje = timezone.now().date()

            context = {
                'qtd_dias' : ferias.qtd_dias,
                'qtd_dias_escrito' : qtd_dias_escrito(ferias.qtd_dias),
                'data_inicio' : ferias.data_inicio.strftime("%d/%m/%Y"),
                'data_termino' : ferias.data_termino.strftime("%d/%m/%Y"),
                'dia_hj' : hoje.day,
                'mes_hj' : mes_escrito(hoje.month),
                'ano_hj' : hoje.year,
                'nome' : ferias.trabalhador.nome,
                'matricula' : ferias.trabalhador.matricula,
                'funcao' : ferias.trabalhador.funcao,
                'setor' : ferias.trabalhador.setor.nome

            }
            return Render.render('template_ferias.html', context)


class LicencaPDF(LoginRequiredMixin, View):

    login_url = '/entrar/'
    redirect_field_name ="index"

    def get(self, request, licenca_id):
        try:
            licenca = LicencaPremio.objects.get(id=licenca_id)
        except:
            messages.error(request, "Não há licença-prêmio com id %d" % licenca_id)
            return redirect('licenca_premio')

        if not licenca.deferida:
            messages.error(request, "A licença(id=%d) solicitada foi deferida e não pode ser impressa" % licenca_id)
            return redirect('licenca_premio')

        elif licenca.fruida:
            messages.error(request, "A licença(id=%d) já foi fruida" % licenca_id)
            return redirect('licenca_premio')

        else:

            hoje = timezone.now().date()

            context = {
                'data_inicio' : licenca.data_inicio.strftime("%d/%m/%Y"),
                'data_termino' : licenca.data_termino.strftime("%d/%m/%Y"),
                'dia_hj' : hoje.day,
                'mes_hj' : mes_escrito(hoje.month),
                'ano_hj' : hoje.year,
                'nome' : licenca.trabalhador.nome,
                'matricula' : licenca.trabalhador.matricula,
                'funcao' : licenca.trabalhador.funcao,
                'setor' : licenca.trabalhador.setor.nome

            }
            return Render.render('template_licenca.html', context)



class AutorizacaoHE(LoginRequiredMixin, View):

    login_url = '/entrar/'
    redirect_field_name ="index"

    def get(self, request, trabalhador_id):
        try:
            trabalhador = Trabalhador.objects.get(id=trabalhador_id)
        except:
            messages.error(request, "Não há trabalhador com id %d" % trabalhador_id)
            return redirect('trabalhadores')


        context = {
            'trabalhador':trabalhador,
        }
        return Render.render('autorizacao_he.html', context)

    def post(self, request, trabalhador_id=-666):
        print(request.POST['trabalhador_id'])
        try:
            trabalhador = Trabalhador.objects.get(id=int(request.POST['trabalhador_id']))
        except:
            messages.error(request, "Não há trabalhador com tal id")
            return redirect('trabalhadores')

        context = {
            'trabalhador' : trabalhador,
        }
        return Render.render('autorizacao_he.html', context)







def proximas_folgas():
    hoje = timezone.now().date()
    folgas = []
    limite_dias = 3

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
    limite_dias = 3

    #como o  tipo 'f' não foi especificado, e por LicencaPremio ser subclasse de Ferias, os dois tipos serão listados na próxima linha
    folgas = Ferias.objects.filter( Q(deferida=True) & Q(data_termino__gt=hoje) & Q(data_termino__lte=hoje+timedelta(days=limite_dias)))
    abonos = Abono.objects.filter(Q(deferido=True) & Q(data=hoje))
    folgas = list(chain(abonos, folgas))

    print('antes do sort', folgas)
    folgas = sorted( folgas, key=lambda obj: obj.data_inicio if "data_inicio" in dir(obj) else obj.data)
    print('retornos', folgas)

    return folgas


def em_andamento():
    hoje = timezone.now().date()
    folgas = []

    #como o  tipo 'f' não foi especificado, e por LicencaPremio ser subclasse de Ferias, os dois tipos serão listados na próxima linha
    folgas = Ferias.objects.filter( Q(deferida=True) & Q(data_inicio__lte=hoje) & Q(data_termino__gte=hoje))
    abonos = Abono.objects.filter(Q(deferido=True) & Q(data=hoje))
    folgas = list(chain(abonos, folgas))

    print('antes do sort', folgas)
    folgas = sorted( folgas, key=lambda obj: obj.data_inicio if "data_inicio" in dir(obj) else obj.data)
    print('retornos', folgas)

    return folgas

def qtd_dias_escrito(dias):
    return 'quinze' if dias == 15 else 'trinta'


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
