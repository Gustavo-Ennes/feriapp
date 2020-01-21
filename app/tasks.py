from app.models import *
from datetime import timedelta
from django.utils import timezone

'''
processo em segundo plano que atualiza a situação do trabalhador
verificando se ele está de férias no dia, ou abonando ou de licenças
'''


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
            if f.data_inicio <= hoje and hoje < f.data_termino and f.deferida:
                trabalhador.situacao = 'ferias'
                break

        for f in licencas:
            if f.data_inicio <= hoje and hoje < f.data_termino and f.deferida:
                trabalhador.situacao = 'licenca'
                break

        for f in abonos:
            if f.data == hoje and f.deferido:
                trabalhador.situacao = 'abono'
                break

        if atestado:
            trabalhador.situacao = 'atestado'

        if trabalhador.situacao == "processando":
            trabalhador.situacao = "ativo"

        trabalhador.save()

    print("Worker: finalizado.")
