from app.models import *
from datetime import timedelta
from django.utils import timezone

'''
processo em segundo plano que atualiza a situação do trabalhador
verificando se ele está de férias no dia, ou abonando ou de licenças
'''


def atualiza_lembretes():
    if timezone.now().date().day == 1:
        for lembrete in Lembrete.objects.all():
            lembrete.mostrado_esse_mes = False
            lembrete.save()


def atualiza_situacoes_trabalhadores():
    hoje = timezone.now().date()

    print("Worker: ciclo iniciado.")
    for trabalhador in Trabalhador.objects.all():
        ferias = Ferias.objects.filter(trabalhador=trabalhador)
        licencas = LicencaPremio.objects.filter(trabalhador=trabalhador)
        abonos = Abono.objects.filter(trabalhador=trabalhador)
        atestado = trabalhador.situacao == "atestado"
        trabalhador.situacao = "processando"

        for f in ferias:
            if not f.fruida:
                print(type(f.data_inicio))
                if f.data_inicio <= hoje and hoje < f.data_termino and f.deferida:
                    trabalhador.situacao = 'ferias'
                    break
                elif f.data_termino <= hoje:
                    f.fruida = True
                    f.save()

        for f in licencas:
            if not f.fruida:
                if f.data_inicio <= hoje and hoje < f.data_termino and f.deferida:
                    trabalhador.situacao = 'licenca'
                    break
                elif f.data_termino <= hoje:
                    f.fruida = True
                    f.save()

        for f in abonos:
            if not f.fruido:
                if f.data == hoje and f.deferido:
                    trabalhador.situacao = 'abono'
                    break
                elif f.data < hoje:
                    f.fruido = True
                    f.save()

        if atestado:
            trabalhador.situacao = 'atestado'

        if trabalhador.situacao == "processando":
            trabalhador.situacao = "ativo"

        trabalhador.save()

    print("Worker: finalizado.")
