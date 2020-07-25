import os
from itertools import chain

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import FileResponse
from django.shortcuts import render, redirect

from app.forms import *
from feriapp.settings import PROJECT_ROOT
from .pdf import PDFFactory
from .tasks import *

lembretes_exibidos = False


def verifica_conf():
    try:
        Conf.objects.get(id=1)
    except:
        Conf.objects.create()


@login_required(login_url='/entrar/')
def index(request):
    verifica_conf()

    if not request.user.groups.filter(Q(name='ferias') | Q(name='relatorio')):
        try:
            trabalhador = Trabalhador.objects.get(Q(user=request.user))
            return redirect('trabalhador', trabalhador_id=trabalhador.id)
        except Exception as e:
            print(e)
            messages.error(request, "O trabalhador não possui usuário para acesso ao site")
            return redirect('sair')
    else:
        context = {
            'FeriasForm': FeriasForm(),
            'LicencaPremioForm': LicencaPremioForm(),
            'AbonoForm': AbonoForm(),
            'TrabalhadorForm': TrabalhadorForm(),
            'SetorForm': SetorForm(),
            'trabalhadores': Trabalhador.objects.all(),
            'index': True,
            'proximas_folgas': proximas_folgas(),
            'proximos_retornos': proximos_retornos(),
            'em_andamento': em_andamento(),
            'AutorizacaoForm': AutorizacaoForm(),
            'lembretes_exibidos': lembretes_exibidos,
            'relatorios': Relatorio.vigentes.em_aberto(),
            'lembretes': Lembrete.objects.all(),
            'data': datetime.now().date(),
            'conf': Conf.objects.get(id=1)

        }

        atualiza_situacoes_trabalhadores()
        atualiza_lembretes()

        return render(request, 'index.html', context)


@login_required(login_url='/entrar/')
@permission_required('app.add_relatorio')
def divide_linha(request):
    if request.method == "POST":
        relatorios = []
        relatorio = Relatorio.vigentes.em_aberto().get(id=int(request.POST['relatorio_id']))
        linha = LinhaRelatorio.objects.get(id=int(request.POST['linha_id']))
        d = {}
        for k in request.POST.keys():
            if 'relatorio-' in k:
                relatorio_id = int(k.split('-')[1])
                d[relatorio_id] = request.POST[k]
        relatorio.linhas.remove(linha)
        for relatorio_id, horas in d.items():
            r = Relatorio.vigentes.em_aberto().get(id=relatorio_id)
            if r != relatorio:
                r.linhas.add(
                    LinhaRelatorio.objects.create(
                        trabalhador=linha.trabalhador,
                        horas_extras=horas
                    )
                )
            else:
                r.linhas.add(
                    LinhaRelatorio.objects.create(
                        trabalhador=linha.trabalhador,
                        horas_extras=horas,
                        adicional_noturno=linha.adicional_noturno,
                        faltas=linha.faltas,
                    )
                )

        messages.success(request, "Você dividiu uma linha do relatório do(a) %s entre %d relatórios." % (
            relatorio.setor.nome, len(d)))

        linha.delete()
    return redirect('relatorios')


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def conf(request):
    if request.method == "GET":
        context = {
            'ConfForm': ConfForm(instance=Conf.objects.get(id=1)),
        }
        return render(request, 'conf.html', context)
    elif request.method == 'POST':
        conf = ConfForm(request.POST, instance=Conf.objects.get(id=1))
        if conf.is_valid():
            conf.save()
            messages.success(request, "Você atualizou as suas configurações.")
            return redirect('index')


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def ferias(request):
    hoje = timezone.now().date()
    context = {
        'futuras': Ferias.objects.filter(Q(deferida=True) & Q(tipo='f') & Q(data_inicio__gt=hoje)),
        'fruidas': Ferias.fruidas.all(),
        'indeferidas': Ferias.indeferidas.all(),
        'em_andamento': Ferias.em_andamento.all(),
        'tipo': 'ferias',
        'FeriasForm': FeriasForm(),
    }
    return render(request, 'ferias.html', context)


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def licenca_premio(request):
    hoje = timezone.now().date()
    context = {
        'futuras': LicencaPremio.objects.filter(Q(deferida=True) & Q(data_inicio__gt=hoje)),
        'fruidas': LicencaPremio.fruidas.all(),
        'indeferidas': LicencaPremio.indeferidas.all(),
        'em_andamento': LicencaPremio.em_andamento.all(),
        'tipo': 'licenca',
        'LicencaPremioForm': LicencaPremioForm(),
    }
    return render(request, 'licenca.html', context)


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def abono(request):
    hoje = timezone.now().date()
    context = {
        'futuros': Abono.objects.filter(Q(deferido=True) & Q(data__gt=hoje)),
        'fruidos': Abono.fruidos.all(),
        'indeferidos': Abono.indeferidos.all(),
        'em_andamento': Abono.em_andamento.all(),
        'tipo': 'abono',
        'AbonoForm': AbonoForm(),
    }

    return render(request, 'abono.html', context)


@login_required(login_url='/entrar/')
def trabalhador(request, trabalhador_id=None):
    trabalhador = None
    usuario_e_trabalhador = bool(Trabalhador.objects.filter(Q(user=request.user)))
    if usuario_e_trabalhador:
        trabalhador_a_acessar = None
        if 'trabalhador' in request.POST:
            trabalhador_a_acessar = Trabalhador.objects.get(id=int(request.POST['trabalhador']))
        elif trabalhador_id:
            trabalhador_a_acessar = Trabalhador.objects.get(id=trabalhador_id)
        trabalhador = Trabalhador.objects.get(Q(user=request.user))
        if trabalhador is not trabalhador_a_acessar:
            messages.info(request, "Só é permitido ao trabalhador acessar seus próprios dados.")

    elif request.method == "GET":
        if trabalhador_id:
            trabalhador = Trabalhador.objects.get(id=int(trabalhador_id))

    elif request.method == "POST":
        id = int(request.POST['trabalhador'])
        trabalhador = Trabalhador.objects.get(id=id)

    hoje = timezone.now().date()
    horas_por_mes = {}
    try:
        relatorios = Relatorio.objects.filter(Q(linhas__trabalhador=trabalhador))
        for r in relatorios:
            linha = r.linhas.get(Q(trabalhador=trabalhador))
            horas = {}
            if linha.horas_extras > 0 or linha.adicional_noturno > 0 or linha.faltas > 0:
                if linha.horas_extras > 0:
                    horas['horas_extras'] = linha.horas_extras
                if linha.adicional_noturno > 0:
                    horas['adicional_noturno'] = linha.adicional_noturno
                if linha.faltas > 0:
                    horas['faltas'] = linha.faltas
            k = str(r.mes) + '/' + str(r.ano)
            horas_por_mes[k] = horas
    except Exception as e:
        print(e)
        messages.error(request, "Trabalhador não encontrado.")
        return redirect('index')

    finally:
        # se o trabalhador tem horas
        tem_horas = False
        for ref, horas in horas_por_mes.items():
            if horas:
                tem_horas = True
                break

        context = {
            'trabalhador': trabalhador,
            'ferias_em_andamento': Ferias.em_andamento.all().filter(Q(trabalhador=trabalhador)),
            'ferias_futuras': Ferias.objects.filter(
                Q(trabalhador=trabalhador) & Q(deferida=True) & Q(tipo='f') & Q(data_inicio__gt=hoje)),
            'ferias_fruidas': Ferias.fruidas.all().filter(Q(trabalhador=trabalhador)),
            'ferias_indeferidas': Ferias.indeferidas.all().filter(Q(trabalhador=trabalhador)),
            'licencas_em_andamento': LicencaPremio.em_andamento.all().filter(Q(trabalhador=trabalhador)),
            'licencas_futuras': LicencaPremio.objects.filter(
                Q(trabalhador=trabalhador) & Q(deferida=True) & Q(data_inicio__gt=hoje)),
            'licencas_fruidas': LicencaPremio.fruidas.all().filter(Q(trabalhador=trabalhador)),
            'licencas_indeferidas': LicencaPremio.indeferidas.all().filter(Q(trabalhador=trabalhador)),
            'abonos_em_andamento': Abono.em_andamento.all().filter(Q(trabalhador=trabalhador)),
            'abonos_futuros': Abono.objects.filter(
                Q(trabalhador=trabalhador) & Q(deferido=True) & Q(data__gt=hoje)),
            'abonos_fruidos': Abono.fruidos.all().filter(Q(trabalhador=trabalhador)),
            'abonos_indeferidos': Abono.indeferidos.all().filter(Q(trabalhador=trabalhador)),
            'TrabalhadorForm': TrabalhadorFormSemAdmissao(),
            'horas_por_mes': horas_por_mes,
            'tem_horas': tem_horas,
        }
        return render(request, 'trabalhador.html', context)


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def setor(request):
    context = {
        'setores': Setor.objects.all(),
        'SetorForm': SetorForm(),
    }

    return render(request, 'setor.html', context)


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def setor_espec(request):
    if request.method == "POST":
        setor = None
        try:
            setor = Setor.objects.get(id=int(request.POST['setor']))
        except:
            messages.error(request, "Não foi possível localizar tal secretaria.")
            return redirect('index')
        finally:
            context = {
                'setor': setor,
                'trabalhadores': Trabalhador.objects.filter(setor=setor),
            }
            return render(request, 'setor_espec.html', context)


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def marcar_ferias(request):
    if request.method == "POST":
        pdf = None
        temp_pdf = None
        obj = None
        try:
            temp_pdf = os.path.join(PROJECT_ROOT, 'temp/pdf.pdf')
        except Exception as e:
            print('-' * 40, "Warning: Pdf indisponível (%s)" % e, '-' * 40)
            messages.error(request, "Pdf indisponível")
            return redirect("index")

        form = FeriasForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.criado_por = request.user
            obj.save()
            hoje = timezone.now().date()
            if obj and obj.deferida and obj.data_inicio >= hoje:
                messages.success(request, 'Você marcou férias para o servidor %s de %s à %s.' % (
                    obj.trabalhador.nome, obj.data_inicio.strftime("%d/%m/%Y"), obj.data_termino.strftime("%d/%d/%Y")))
                PDFFactory.get_ferias_pdf(obj)
                pdf = open(temp_pdf, 'rb')
                return FileResponse(pdf, filename=temp_pdf)
            else:
                messages.error(request, "O trabalhador não pode tirar férias nessa data por %s." % obj.observacoes)



        else:
            messages.error(request, form.errors)

        return redirect('ferias')


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def marcar_licenca(request):
    if request.method == "POST":
        form = LicencaPremioForm(request.POST)
        obj = None
        if form.is_valid():
            hoje = timezone.now().date()
            obj = form.save()
            obj.criado_por = request.user
            obj.save()
            if obj and obj.deferida and obj.data_inicio >= hoje:
                messages.success(request, 'Você marcou licença-prêmio para o servidor %s de %s à %s.' % (
                    obj.trabalhador.nome, obj.data_inicio.strftime("%d/%m/%Y"), obj.data_termino.strftime("%d/%d/%Y")))
            else:
                messages.error(request,
                               "O trabalhador não pode tirar licença-prêmio nessa data por %s." % obj.observacoes)
                return redirect('licenca_premio')
        else:
            messages.error(request, form.errors)

        return redirect('pdf', tipo='licenca', obj_id=obj.id) if obj.deferida else redirect("licenca_premio")


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def marcar_abono(request):
    if request.method == "POST":
        form = AbonoForm(request.POST)
        if form.is_valid():
            hoje = timezone.now().date()
            obj = form.save()
            obj.criado_por = request.user
            obj.save()
            if obj and obj.deferido:
                if obj.data >= hoje:
                    messages.success(request, 'Você marcou um abono para o servidor %s em %s.' % (
                        obj.trabalhador.nome, obj.data.strftime("%d/%m/%Y")))
                else:
                    messages.warning(request, "Atenção: abono com %s" % obj.observacoes)
            else:
                messages.error(request, "O trabalhador não pode abonar nessa data por %s." % obj.observacoes)
        else:
            messages.error(request, form.errors)

        return redirect('pdf', tipo='abono', obj_id=obj.id) if obj.deferido else redirect("abono")


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def novo_setor(request):
    if request.method == "POST":
        form = SetorForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.criado_por = request.user
            obj.save()
            messages.success(request, 'Você cadastrou um novo setor: %s.' % (obj.nome))
        else:
            messages.error(request, form.errors)

        return redirect("setor")


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def novo_trabalhador(request):
    if request.method == "POST":
        form = TrabalhadorForm(request.POST)
        string = ''
        if form.is_valid():
            obj = form.save()
            obj.criado_por = request.user
            obj.save()
            messages.success(request, 'Você cadastrou um novo trabalhador: %s - %s .' % (obj.nome, obj.funcao))
        else:
            if 'matricula' in form.errors:
                string = 'Servidor não cadastrado: já existe servidor com essa matrícula'
            elif 'nome' in form.errors:
                string = 'Servidor não cadastrado: já existe servidor com esse nome'
            else:
                string = "Erro: " + form.errors

            messages.error(request, string)

        return redirect("trabalhadores")


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def trabalhadores(request):
    trabalhadores = Trabalhador.objects.all()
    context = {
        'trabalhadores': trabalhadores,
        'TrabalhadorFormSemAdmissao': TrabalhadorFormSemAdmissao(),
        "TrabalhadorForm": TrabalhadorForm(),
    }
    return render(request, 'trabalhadores.html', context)


@login_required(login_url='/entrar/')
def pesquisa(request):
    if request.method == "POST":
        hoje = timezone.now().date()
        query = request.POST['query']
        context = {
            'ferias_futuras': Ferias.objects.filter(
                (
                        Q(trabalhador__nome__icontains=query) |
                        Q(trabalhador__funcao__icontains=query) |
                        Q(trabalhador__setor__nome__icontains=query)
                ) &
                Q(deferida=True) &
                Q(data_inicio__gt=hoje) &
                Q(tipo='f')
            ),
            'ferias_fruidas': Ferias.fruidas.all().filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)
            ),
            'ferias_indeferidas': Ferias.indeferidas.all().filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)

            ),
            'licencas_futuras': LicencaPremio.objects.filter(
                (
                        Q(trabalhador__nome__icontains=query) |
                        Q(trabalhador__funcao__icontains=query) |
                        Q(trabalhador__setor__nome__icontains=query)
                ) &
                Q(deferida=True) &
                Q(data_inicio__gt=hoje)
            ),
            'licencas_fruidas': LicencaPremio.fruidas.all().filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)
            ),
            'licencas_indeferidas': LicencaPremio.indeferidas.all().filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)
            ),
            'abonos_futuros': Abono.objects.filter(
                (
                        Q(trabalhador__nome__icontains=query) |
                        Q(trabalhador__funcao__icontains=query) |
                        Q(trabalhador__setor__nome__icontains=query)
                ) &
                Q(deferido=True) &
                Q(data__gt=hoje)
            ),
            'abonos_fruidos': Abono.fruidos.all().filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)
            ),
            'abonos_indeferidos': Abono.indeferidos.all().filter(
                Q(trabalhador__nome__icontains=query) |
                Q(trabalhador__funcao__icontains=query) |
                Q(trabalhador__setor__nome__icontains=query)
            ),
            'trabalhadores': Trabalhador.objects.filter(
                Q(nome__icontains=query) |
                Q(funcao__icontains=query) |
                Q(setor__nome__icontains=query)
            ),
            'setores': Setor.objects.filter(Q(nome__icontains=query)),
            'query': query,
        }
        context['qtd_resultados'] = len(context['licencas_futuras']) + len(context['licencas_fruidas']) + len(
            context['licencas_indeferidas']) + len(context['abonos_fruidos']) + len(context['abonos_futuros']) + len(
            context['abonos_indeferidos']) + len(context['ferias_fruidas']) + len(context['ferias_futuras']) + len(
            context['ferias_indeferidas']) + len(context['trabalhadores']) + len(context['setores'])

        return render(request, 'pesquisa.html', context)


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
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
                messages.success(request, "Você editou a data do(a) %s do servidor %s para %s." % (
                    verbose_name, obj.trabalhador.nome, data))
                obj.observacoes = "reagendado"
            else:
                obj.data = data_antiga
                messages.error(request, "O abono não pode ser editado por %s. A data original (%s) foi mantida" % (
                    obj.observacoes, obj.data.strftime("%d/%m/%Y")))
        elif tipo == ("ferias" or 'licenca'):
            if obj.deferida:
                messages.success(request, "Você editou a data do(a) %s do servidor %s para %s." % (
                    verbose_name, obj.trabalhador.nome, data))
                obj.observacoes = "reagendada"
            else:
                obj.data_inicio = data_antiga
                obj.data_termino = obj.data_inicio + timedelta(days=obj.qtd_dias - 1)
                messages.error(request, "O(a) %s não pode ser editado por %s. A data original (%s) foi mantida" % (
                    verbose_name, obj.observacoes, obj.data_inicio.strftime("%d/%m/%Y")))

        obj.save()

        return redirect(return_name)


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def editar_trabalhador(request):
    if request.method == "POST":
        trabalhador = Trabalhador.objects.get(id=int(request.POST['id']))
        form = TrabalhadorFormSemAdmissao(request.POST, instance=trabalhador)
        obj = form.save()
        messages.success(request, "Você editou os dados de %s." % (trabalhador.nome))
        return redirect("trabalhadores")


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
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
        messages.success(request, "Você deletou o setor %s." % (setor.nome))
        setor.delete()
        return redirect("setor")


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def excluir_trabalhador(request):
    if request.method == "POST":
        trabalhador = Trabalhador.objects.get(id=int(request.POST['trabalhador_id']))
        messages.success(request, "Você excluir o servidor %s." % (trabalhador.nome))
        trabalhador.delete()
        return redirect("trabalhadores")


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
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
        obj.save(validacao=False)
        messages.success(request, mensagem)

        return redirect(voltar_para)


def entrar(request):
    if request.method == "GET":
        context = {
            'LoginForm': LoginForm(),
        }
        return render(request, 'login.html', context)

    elif request.method == "POST":
        logout(request)
        username = request.POST['usuario']
        password = request.POST['senha']
        remember_me = True if 'remember_me' in request.POST else False

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                name = user.username if user.groups.count() > 0 else Trabalhador.objects.get(
                    Q(matricula=user.username)).nome
                messages.success(request, 'Bem-vindo(a), %s' % name)

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


@login_required(login_url='/entrar/')
def autorizacao(request):
    context = {
        'AutorizacaoForm': AutorizacaoForm(),
    }
    return render(request, 'justificativas_he.html', context)


@login_required(login_url='/entrar/')
@permission_required('app.add_relatorio')
def soma_justificativas(request):
    data = datetime.now()
    if request.method == 'GET':
        if not Relatorio.vigentes.finalizados():
            relatorios_deste_mes = Relatorio.objects.filter(
                Q(criado_em__year=data.year) & Q(criado_em__month=data.month))
            if not relatorios_deste_mes:
                context = {
                    'trabalhadores': Trabalhador.objects.all(),
                    'setores': Setor.objects.all(),
                }
                return render(request, 'soma_justificativas.html', context)
            else:
                for relatorio in relatorios_deste_mes:
                    if relatorio.estado == 'terminado':
                        messages.warning(request, "Os relatórios estão concluídos. Vá em relatórios para editá-los")
                        return redirect("relatorios")
                messages.warning(request,
                                 "O relatório deste mês já foi gerado. Confira as horas no extrato de ponto, adicione as faltas e adicional noturno")
                return redirect('soma_horas')
        else:
            messages.warning(request, "Você já finalizou os relatórios deste meŝ")
            return redirect('relatorios')

    elif request.method == 'POST':
        trabalhadores = Trabalhador.objects.all()

        for trabalhador in trabalhadores:
            string = str(trabalhador.id) + "horas"
            # busco por relatórios desse mês
            relatorio = busca_relatorio(trabalhador.setor)
            if not relatorio:
                # se não há eu gero
                relatorio = gera_relatorio_em_branco(trabalhador.setor, 1)

            if string in request.POST:
                linha = LinhaRelatorio.objects.create(
                    trabalhador=trabalhador,
                    horas_extras=float(request.POST[string])
                )
                relatorio.linhas.add(linha)
                if relatorio.estado == 'vazio':
                    relatorio.estado = 'justificativas'

                relatorio.save()

        for setor in Setor.objects.all():
            string = "num_oficio-" + str(setor.id)
            if string in request.POST:
                relatorio = Relatorio.vigentes.em_aberto().get(setor=setor)
                if relatorio:
                    relatorio.num_oficio = request.POST[string]
                    relatorio.save()

        messages.success(request, "Soma das justificativas concluída")
        return redirect('index')


def busca_relatorio(setor):
    try:
        return Relatorio.vigentes.em_aberto().get(Q(setor=setor))
    except Exception as e:
        print("> Não há relatórios deste mês ainda, eles serão gerados")
        return None


@login_required(login_url='/entrar/')
@permission_required('app.add_relatorio')
def soma_horas(request):
    # ver se tenho relatorio desse mes
    if not Relatorio.vigentes.finalizados():
        relatorios_deste_mes = Relatorio.vigentes.em_aberto()

        if not relatorios_deste_mes:
            messages.warning(request, "Não há relatórios deste mês. Some as justificativas primeiramente")
            return redirect('soma_justificativas')

        for relatorio in relatorios_deste_mes:
            string = 'num_oficio-' + str(relatorio.setor.id)
            if string in request.POST:
                relatorio.num_oficio = request.POST[string]
                relatorio.save()
            if relatorio.estado == "vazio":
                messages.warning(request,
                                 "Algum relatório deste mês não possui as somas das justificativas ainda. Some as justificativas")
                return redirect('soma_justificativas')

        if request.method == "GET":

            for relatorio in relatorios_deste_mes:
                if relatorio.estado == 'terminado':
                    messages.info(request, "Os relatórios foram terminados. Edite-os em Relatórios")
                    return redirect('relatorios')

            context = {
                'trabalhadores': Trabalhador.objects.all(),
                'setores': Setor.objects.all(),
                'relatorios': relatorios_deste_mes,
            }
            return render(request, 'soma_horas.html', context)

        elif request.method == "POST":

            trabalhadores = Trabalhador.objects.all()
            [print("\n%s: %s" % (k, v)) for k, v in request.POST.items()]
            for trabalhador in trabalhadores:
                # achar a linha do relatório desse mês correspondente ao trabalhador
                relatorio = busca_relatorio(trabalhador.setor)
                horas_extras_str = request.POST[str(trabalhador.id) + 'horas']
                horas_extras = float(horas_extras_str.replace(',', '.'))
                adc_noturno_str = request.POST[str(trabalhador.id) + 'adc_noturno']
                adc_noturno = float(adc_noturno_str.replace(',', '.'))
                faltas = int(request.POST[str(trabalhador.id) + 'faltas'])
                linha = None

                try:
                    linha = relatorio.linhas.get(Q(trabalhador=trabalhador))
                except Exception as e:
                    print(e)

                    linha = LinhaRelatorio.objects.create(
                        horas_extras=horas_extras,
                        adc_noturno=adc_noturno,
                        faltas=faltas
                    )

                conf = Conf.objects.get(id=1)

                linha.horas_extras = horas_extras
                linha.adicional_noturno = adc_noturno if not conf.calculo_de_adicional else adc_noturno * conf.ADC_CONST
                linha.faltas = faltas
                linha.save()
                relatorio.save()

            for relatorio in relatorios_deste_mes:
                relatorio.estado = "terminado"
                relatorio.save()
            messages.success(request,
                             "Relatórios deste mês foram terminados. Eles ainda podem ser editados. Quando acabarem as edições, clique em 'Finalizar Relatórios em Aberto'")
            return redirect('relatorios')
    else:
        messages.warning(request, "Os relatórios deste mês já foram finalizados")
        return redirect('relatorios')


@login_required(login_url='/entrar/')
@permission_required('app.add_ferias')
def relatorios(request):
    data = timezone.now()
    data = data.replace(day=1)
    context = {
        'relatorios_em_aberto': Relatorio.vigentes.em_aberto(),
        'relatorios_finalizados': Relatorio.vigentes.finalizados(),
        'relatorios_finalizados_antigos': Relatorio.objects.filter(Q(estado='oficial') & Q(criado_em__lt=data)),
        'qtd_trabalhadores': Trabalhador.objects.count(),
    }
    return render(request, 'relatorios.html', context)


@login_required(login_url='/entrar/')
@permission_required('app.add_relatorio')
def finalizar_relatorios(request):
    if request.method == 'POST':
        relatorios = Relatorio.vigentes.em_aberto()
        lembrete = Lembrete.objects.get(id=1)

        for r in relatorios:
            r.data_fechamento = datetime.now().date()
            r.estado = 'oficial'
            r.save()

        lembrete.mostrado_esse_mes = True
        lembrete.save()

        messages.success(request, "%d relatórios foram finalizados e é impossível editá-los" % relatorios.count())
        return redirect('relatorios')


def imprime_sem_previa(pdf):
    import platform
    if platform.system() == 'Linux':
        stream = os.popen('lpstat -p -d')
        if stream:
            printer_name = stream.read().split(": ")[1]
            os.system('lpr -P %s %s' % (printer_name, os.path.join(PROJECT_ROOT, 'temp/pdf.pdf')))



@login_required(login_url='/entrar/')
def pdf(request, tipo, obj_id):
    temp_pdf = None
    obj = None
    try:
        temp_pdf = os.path.join(PROJECT_ROOT, 'temp/pdf.pdf')
    except Exception as e:
        print('-' * 40, "Warning: Pdf indisponível (%s)" % e, '-' * 40)
        messages.error(request, "Pdf indisponível")
        return redirect("index")

    if request.method == "POST":

        if tipo == 'aviso':
            obj = {
                'orientacao': request.POST['orientacao'],
                'tipo': request.POST['tipo'],
                'titulo': request.POST['titulo'],
                'conteudo': request.POST['conteudo'],
                'observacoes': request.POST['observacoes'],
            }

        elif tipo == 'sexta_parte':
            t = Trabalhador.objects.get(id=int(request.POST['trabalhador']))
            text = "O(s) campo(s)"
            erro = False
            if t.rg:
                if t.rg != request.POST['rg']:
                    text += "->RG\n "
                    erro = True
            if t.cpf:
                if t.cpf != request.POST['cpf']:
                    text += "->CPF\n"
                    erro = True

            if erro:
                messages.error(request, text + " não são iguais aos do cadastro do servidor, Confira os documentos.")
                return redirect("index")

            text = "O(s) campo(s):\n"
            salvar = False
            if not t.rg:
                text += "->RG\n"
                t.rg = request.POST['rg']
                salvar = True
            if not t.cpf:
                text += "->CPF\n"
                t.cpf = request.POST['cpf']
                salvar = True

            if salvar:
                t.save()

            obj = {
                'trabalhador': t,
                'rg': t.rg,
                'cpf': t.cpf,
            }
            # se o trabalhador não tem 20 anos de trampo
            if t.data_admissao > timezone.now() - timedelta(days=20 * 365):
                messages.warning(request, "O trabalhador informado não possui 20 anos de serviços prestados")
                return redirect('index')

        elif tipo == 'atestado':
            t = Trabalhador.objects.get(id=int(request.POST['trabalhador']))
            text = 'O(s) campo(s):\n '
            erro = False

            if t.rg:
                if t.rg != request.POST['rg']:
                    text += "->RG\n "
                    erro = True
            if t.cpf:
                if t.cpf != request.POST['cpf']:
                    text += "->CPF\n"
                    erro = True
            if t.ctps:
                if t.ctps != request.POST['ctps']:
                    text += "->CTPS\n"
                    erro = True
            if t.ctps_serie:
                if t.ctps_serie != request.POST['ctps_serie']:
                    text += "->Série da CTPS\n"
                    erro = True

            if erro:
                text += "não são iguais aos que constam no cadastro do trabalhador. Verifique a documentação."
                messages.error(request, text)
                return redirect('index')

            text = "O(s) campo(s):\n"
            salvar = False
            if not t.rg:
                text += "->RG\n"
                t.rg = request.POST['rg']
                salvar = True
            if not t.cpf:
                text += "->CPF\n"
                t.cpf = request.POST['cpf']
                salvar = True
            if not t.ctps:
                text += "->CPTS\n"
                t.ctps = request.POST['ctps']
                salvar = True
            if not t.ctps_serie:
                text += "->Série CTPS\n"
                t.ctps_serie = request.POST['ctps_serie']
                salvar = True

            if salvar:
                t.save()
                messages.info(request, text + " foram incluídos nos registros do trabalhador")

            obj = {
                'trabalhador': t,
                'rg': request.POST['rg'],
                'cpf': request.POST['cpf'],
                'ctps': request.POST['ctps'],
                'ctps_serie': request.POST['ctps_serie']
            }

        elif tipo == "justificativa":

            try:
                obj = Trabalhador.objects.get(id=int(request.POST['trabalhador']))
            except Exception as e:
                print('-' * 40, "\nWarning: Erro em obter trabalhador: (%s)\n" % e, '-' * 40)
                messages.error(request, "Erro em obter trabalhador: %s" % e)
                return redirect('index')

        elif tipo == 'pesquisa':
            query = request.POST['query']
            hoje = datetime.now().date()
            obj = {
                'label': 'Pesquisa: %s' % query,
                'ferias_futuras': Ferias.objects.filter(
                    (
                            Q(trabalhador__nome__icontains=query) |
                            Q(trabalhador__funcao__icontains=query) |
                            Q(trabalhador__setor__nome__icontains=query)
                    ) &
                    Q(deferida=True) &
                    Q(data_inicio__gt=hoje) &
                    Q(tipo='f')
                ),
                'ferias_fruidas': Ferias.fruidas.all().filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ),
                'ferias_indeferidas': Ferias.indeferidas.all().filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)

                ),
                'ferias_em_andamento': Ferias.em_andamento.all().filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)

                ),
                'licencas_futuras': LicencaPremio.objects.filter(
                    (
                            Q(trabalhador__nome__icontains=query) |
                            Q(trabalhador__funcao__icontains=query) |
                            Q(trabalhador__setor__nome__icontains=query)
                    ) &
                    Q(deferida=True) &
                    Q(data_inicio__gt=hoje)
                ),
                'licencas_fruidas': LicencaPremio.fruidas.all().filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ),
                'licencas_indeferidas': LicencaPremio.indeferidas.all().filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ),
                'licencas_em_andamento': LicencaPremio.em_andamento.all().filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ),
                'abonos_futuros': Abono.objects.filter(
                    (
                            Q(trabalhador__nome__icontains=query) |
                            Q(trabalhador__funcao__icontains=query) |
                            Q(trabalhador__setor__nome__icontains=query)
                    ) &
                    Q(deferido=True) &
                    Q(data__gt=hoje)
                ),
                'abonos_fruidos': Abono.fruidos.all().filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ),
                'abonos_indeferidos': Abono.indeferidos.all().filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ),
                'abonos_em_andamento': Abono.em_andamento.all().filter(
                    Q(trabalhador__nome__icontains=query) |
                    Q(trabalhador__funcao__icontains=query) |
                    Q(trabalhador__setor__nome__icontains=query)
                ),
                'trabalhadores': Trabalhador.objects.filter(
                    Q(nome__icontains=query) |
                    Q(funcao__icontains=query) |
                    Q(setor__nome__icontains=query)
                ),
                'setores': Setor.objects.filter(Q(nome__icontains=query)),
                'query': query,
            }

        elif tipo == 'abono':
            hoje = datetime.now().date()
            obj = {
                'abonos_futuros': Abono.objects.filter(Q(deferido=True) & Q(data__gt=hoje)),
                'abonos_em_andamento': Abono.em_andamento.all(),
                'abonos_fruidos': Abono.fruidos.all(),
                'abonos_indeferidos': Abono.indeferidos.all(),
            }
        elif tipo == 'ferias':
            hoje = datetime.now().date()
            obj = {
                'ferias_futuras': Ferias.objects.filter(Q(tipo='f') & Q(deferida=True) & Q(data_inicio__gt=hoje)),
                'ferias_em_andamento': Ferias.em_andamento.all(),
                'ferias_fruidas': Ferias.fruidas.all(),
                'ferias_indeferidas': Ferias.indeferidas.all(),
            }
        elif tipo == 'licenca':
            hoje = datetime.now().date()
            obj = {
                'licencas_futuras': LicencaPremio.objects.filter(Q(deferida=True) & Q(data_inicio__gt=hoje)),
                'licencas_em_andamento': LicencaPremio.em_andamento.all(),
                'licencas_fruidas': LicencaPremio.fruidas.all(),
                'licencas_indeferidas': LicencaPremio.indeferidas.all(),
            }
        elif tipo == 'setores':
            d = {}
            for setor in Setor.objects.all():
                d[setor.nome] = setor.trabalhador_set.all()
            obj = {
                'setor_dict': d,
            }
        elif tipo == 'trabalhadores':
            obj = {
                'trabalhadores': Trabalhador.objects.all()
            }
        else:
            try:
                obj = Trabalhador.objects.get(id=int(request.POST['trabalhador']))
            except Exception as e:
                print('-' * 40, "\nWarning:Não há trabalhador com tal id (%s)\n" % e, '-' * 40)
                messages.error(request, "Não há trabalhador com tal id")
                return redirect('index')

    elif request.method == "GET":
        model_name = ""
        hoje = datetime.now().date()

        try:
            if tipo == 'relacao_abono':

                if verifica_grupo(request.user, 'relatorio'):
                    # seto o primeiro dia do mês
                    primeiro_dia_do_mes = hoje.replace(day=1)
                    ultimo_dia_do_mes = hoje
                    # e descubro o último
                    while ultimo_dia_do_mes.month == hoje.month:
                        ultimo_dia_do_mes = ultimo_dia_do_mes + timedelta(days=1)
                    ultimo_dia_do_mes -= timedelta(days=1)
                    obj = Abono.objects.filter(
                        Q(deferido=True) & Q(data__gte=primeiro_dia_do_mes) & Q(data__lte=ultimo_dia_do_mes))

                    # se obj_id == 1 quer dizer que não quero mais ver esse aviso, então
                    if obj_id == 1:
                        l = Lembrete.objects.get(id=2)
                        l.mostrado_esse_mes = True
                        l.save()
                else:
                    messages.error(request, "Permissão negada")
                    return redirect('abono')

            if tipo == 'relatorio':
                if verifica_grupo(request.user, 'relatorio'):
                    obj = Relatorio.objects.get(id=int(obj_id))
                    model_name = "Relatório"
                else:
                    messages.error(request, "Permissão negada")
                    return redirect('relatorios')
            if tipo == 'relatorio-copia':
                obj = Relatorio.objects.get(id=int(obj_id))
                model_name = "Relatório"
            if tipo == 'ferias':
                obj = Ferias.objects.get(id=int(obj_id))
                model_name = "Feŕias"
            if tipo == 'licenca':
                obj = LicencaPremio.objects.get(id=int(obj_id))
                model_name = "Licença Prêmio"
            if tipo == 'abono':
                obj = Abono.objects.get(id=int(obj_id))
                model_name = "Abono"
            if tipo == 'justificativa':
                obj = Trabalhador.objects.get(id=int(obj_id))
                model_name = "Justificativa"
            if tipo == 'trabalhador_historico':
                trabalhador = Trabalhador.objects.get(id=int(obj_id))
                model_name = 'Trabalhador'
                obj = {
                    'label': "Histórico do servidor %s" % trabalhador.nome,
                    'ferias_em_andamento': Ferias.em_andamento.all().filter(Q(trabalhador=trabalhador)),
                    'ferias_futuras': Ferias.objects.filter(
                        Q(trabalhador=trabalhador) & Q(deferida=True) & Q(tipo='f') & Q(data_inicio__gt=hoje)),
                    'ferias_fruidas': Ferias.fruidas.all().filter(Q(trabalhador=trabalhador)),
                    'ferias_indeferidas': Ferias.indeferidas.all().filter(Q(trabalhador=trabalhador)),
                    'abonos_em_andamento': Abono.em_andamento.all().filter(Q(trabalhador=trabalhador)),
                    'abonos_futuros': Abono.objects.filter(
                        Q(trabalhador=trabalhador) & Q(deferido=True) & Q(data__gte=hoje)),
                    'abonos_fruidos': Abono.fruidos.all().filter(Q(trabalhador=trabalhador)),
                    'abonos_indeferidos': Abono.indeferidos.all().filter(Q(trabalhador=trabalhador)),
                    'licencas_em_andamento': LicencaPremio.em_andamento.all().filter(Q(trabalhador=trabalhador)),
                    'licencas_futuras': LicencaPremio.objects.filter(
                        Q(trabalhador=trabalhador) & Q(deferida=True) & Q(data_inicio__gt=hoje)),
                    'licencas_fruidas': LicencaPremio.fruidas.all().filter(Q(trabalhador=trabalhador)),
                    'licencas_indeferidas': LicencaPremio.indeferidas.all().filter(Q(trabalhador=trabalhador)),
                    'horas': LinhaRelatorio.objects.filter(Q(trabalhador=trabalhador)),
                    'trabalhador': trabalhador,
                }
            if tipo == 'setor_historico':
                setor = Setor.objects.get(id=int(obj_id))
                model_name = 'Setor'
                obj = {
                    'label': 'Histórico do setor %s' % setor.nome,
                    'trabalhadores': setor.trabalhador_set.all(),
                    'setor': setor
                }
        except Exception as e:
            print('-' * 40, "\nWarning:%s (%s)\n" % (model_name, e), '-' * 40)
            messages.error(request, "%s: %s" % (model_name, e))
            return redirect('index')

    # obj vazio aqui
    if tipo == 'materiais':
        obj = 'any'
    if obj is not None:
        if tipo == 'aviso':
            PDFFactory.get_aviso_pdf(obj)
        elif tipo == 'materiais':
            PDFFactory.get_materiais_pdf()
        if tipo == 'sexta_parte':
            PDFFactory.get_sexta_parte_pdf(obj)
        elif tipo == 'atestado':
            PDFFactory.get_atestado_trabalho(obj)
        elif tipo == 'relacao_abono':
            if obj:
                PDFFactory.get_relacao_abono_pdf(obj)
                l = Lembrete.objects.get(id=2)
                if not l.mostrado_esse_mes:
                    l.mostrado_esse_mes = True
                    l.save()
            else:
                messages.warning(request, "Não há abonos para listar")
                return redirect('abono')
        elif tipo == 'relatorio':
            PDFFactory.get_relatorio_pdf(obj, copia=False)
        elif tipo == 'relatorio-copia':
            PDFFactory.get_relatorio_pdf(obj, copia=True)
        elif tipo == "abono" and request.method == "GET":
            PDFFactory.get_abono_pdf(obj)
        elif tipo == 'abono' and request.method == 'POST':
            PDFFactory.get_abonos_pdf(obj)
        elif tipo == "licenca" and request.method == 'GET':
            PDFFactory.get_licenca_pdf(obj)
        elif tipo == 'licenca' and request.method == "POST":
            PDFFactory.get_licencas_pdf(obj)
        elif tipo == "ferias" and request.method == 'GET':
            PDFFactory.get_ferias_pdf(obj)
        elif tipo == 'ferias' and request.method == "POST":
            PDFFactory.get_ferias_gerais_pdf(obj)
        elif tipo == 'justificativa':
            PDFFactory.get_justificativa_pdf(obj)
        elif tipo == "trabalhador_historico":
            PDFFactory.get_trabalhador_historico_pdf(obj)
        elif tipo == 'setor_historico':
            PDFFactory.get_setor_historico_pdf(obj)
        elif tipo == 'pesquisa':
            PDFFactory.get_search_pdf(obj)
        elif tipo == 'setores':
            PDFFactory.get_setores_pdf(obj)
        elif tipo == 'trabalhadores':
            PDFFactory.get_trabalhadores_pdf(obj)

        pdf = open(temp_pdf, 'rb')
        return FileResponse(pdf, filename=temp_pdf)


@login_required(login_url='/entrar/')
@permission_required('app.add_relatorio')
def relatorio_edicao(request, relatorio_id):
    if request.method == 'GET':
        data = datetime.now()
        relatorio = Relatorio.objects.get(id=relatorio_id)
        relatorios = Relatorio.vigentes.all()

        context = {
            'relatorio': relatorio,
            'relatorios': relatorios.exclude(id=relatorio_id),
            'todos_relatorios': relatorios
        }

        return render(request, 'relatorio_edicao.html', context)


@login_required(login_url='/entrar/')
@permission_required('app.add_relatorio')
def modifica_relatorio(request):
    relatorio = None
    if request.method == 'POST':
        tipo = request.POST['tipo']
        linha_id = None
        linha = None

        if 'linha_id' in request.POST:
            linha_id = int(request.POST['linha_id'])

            try:
                linha = LinhaRelatorio.objects.get(id=linha_id)
            except:
                messages.error(request, "Não existe tal linha no banco de dados")
                return redirect('relatorios')

            relatorio = Relatorio.vigentes.em_aberto().filter(Q(linhas__trabalhador=linha.trabalhador))
            if relatorio:
                if relatorio[0].estado == 'oficial':
                    messages.warning(request, "Os relatórios deste mês já foram finalizados e não podem ser editados")
                    return redirect('relatorios')

        if tipo == 'num_oficio':
            relatorio_id = int(request.POST['relatorio_id'])
            relatorio = Relatorio.vigentes.all().get(id=relatorio_id)
            num_oficio = request.POST['num_oficio']
            relatorio.num_oficio = num_oficio
            relatorio.save()
            messages.success(request,
                             "Você trocou o número de ofício do relatório #%d para %s" % (relatorio_id, num_oficio))
            return redirect('relatorio_edicao', relatorio_id=relatorio.id)

        elif tipo == 'horas_extras':

            if linha:
                horas = float(request.POST['qtd_horas_extras-%s' % str(linha_id)])
                if horas:
                    linha.horas_extras = horas
                    linha.save()
                    messages.success(request, "Você editou as horas extras de %s" % linha.trabalhador.nome)

        elif tipo == 'adicional_noturno':

            if linha:
                adc = float(request.POST['qtd_adicional_noturno-%s' % str(linha_id)])
                if adc:
                    linha.adicional_noturno = adc
                    linha.save()
                    messages.success(request, "Você editou o adicional noturno de %s" % linha.trabalhador.nome)

        elif tipo == "faltas":

            if linha:
                faltas = int(request.POST['qtd_faltas-%s' % str(linha_id)])
                linha.faltas = faltas
                linha.save()
                messages.success(request, "Você a quantidade de faltas de %s" % linha.trabalhador.nome)

        elif tipo == 'transferencia':
            if linha:
                setor_a_transferir = int(request.POST['transferencia-%s' % str(linha_id)])
                setor_fonte = int(request.POST['relatorio_id'])
                relatorio_alvo = None
                relatorio_fonte = None

                try:
                    relatorio_alvo = Relatorio.objects.get(id=setor_a_transferir)
                    relatorio_fonte = Relatorio.objects.get(id=setor_fonte)
                except Exception as e:
                    messages.error(request, "Erro: %s" % e)

                LinhaRelatorio.transferencia(relatorio_fonte, relatorio_alvo, linha)
                messages.success(request, "A linha %d foi transferida para o relatório alvo" % linha_id)
                return redirect("relatorio_edicao", relatorio_id=relatorio_alvo.id)

        elif tipo == 'excluir':
            if linha:
                messages.success(request, "Você a deletou de a linha de id %d" % (linha.id))
                linha.delete()

        return redirect('relatorio_edicao', relatorio[0].id) if relatorio.count() else redirect('relatorios')


@login_required(login_url='/entrar/')
def atestado(request):
    if request.method == 'GET':
        context = {
            'trabalhadores': Trabalhador.objects.all(),
            'AtestadoForm': AtestadoForm(),
        }
        return render(request, 'atestado.html', context)


@login_required(login_url='/entrar/')
def sexta_parte(request):
    if request.method == "GET":
        context = {
            'trabalhadores': Trabalhador.objects.all(),
        }
        return render(request, 'sexta_parte.html', context)


@login_required(login_url='/entrar/')
def aviso(request):
    if request.method == 'GET':
        context = {
            'AvisoForm': AvisoForm(),
        }
        return render(request, 'aviso.html', context)


###########################################################################################################


def gera_relatorio_em_branco(setor, num_oficio):
    return Relatorio.objects.create(setor=setor, num_oficio=num_oficio)


def proximas_folgas():
    hoje = timezone.now().date()
    folgas = []
    limite_dias = 7

    # como o  tipo 'f' não foi especificado, e por LicencaPremio ser subclasse de Ferias, os dois tipos serão
    # listados na próxima linha
    folgas = Ferias.objects.filter(
        Q(deferida=True) & Q(data_inicio__gt=hoje) & Q(data_inicio__lte=hoje + timedelta(days=limite_dias)))
    abonos = Abono.objects.filter(Q(deferido=True) & Q(data__gt=hoje) & Q(data__lt=hoje + timedelta(days=limite_dias)))
    folgas = list(chain(abonos, folgas))

    folgas = sorted(folgas, key=lambda obj: obj.data_inicio if "data_inicio" in dir(obj) else obj.data)

    return folgas


def proximos_retornos():
    hoje = timezone.now().date()
    folgas = []
    limite_dias = 7

    # como o  tipo 'f' não foi especificado, e por LicencaPremio ser subclasse de Ferias, os dois tipos serão
    # listados na próxima linha
    folgas = Ferias.objects.filter(
        Q(deferida=True) & Q(data_termino__gt=hoje) & Q(data_termino__lte=hoje + timedelta(days=limite_dias)))
    abonos = Abono.objects.filter(Q(deferido=True) & Q(data=hoje))
    folgas = list(chain(abonos, folgas))

    folgas = sorted(folgas, key=lambda obj: obj.data_inicio if "data_inicio" in dir(obj) else obj.data)

    return folgas


def em_andamento():
    hoje = timezone.now().date()
    folgas = []

    # como o  tipo 'f' não foi especificado, e por LicencaPremio ser subclasse de Ferias, os dois tipos serão listados na próxima linha
    folgas = Ferias.objects.filter(Q(deferida=True) & Q(data_inicio__lte=hoje) & Q(data_termino__gte=hoje))
    abonos = Abono.objects.filter(Q(deferido=True) & Q(data=hoje))
    folgas = list(chain(abonos, folgas))

    folgas = sorted(folgas, key=lambda obj: obj.data_inicio if "data_inicio" in dir(obj) else obj.data)

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


def verifica_grupo(user, group_name):
    return bool(user.groups.filter(Q(name=group_name)))
