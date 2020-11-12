import os
import random
from datetime import datetime, timedelta

from django.db.models.query import QuerySet
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate, Image

from feriapp.settings import PROJECT_ROOT, BASE_DIR
from .models import Relatorio, Abono, LicencaPremio, Ferias, Trabalhador, Setor, LinhaRelatorio


class RandomStuff:

    @staticmethod
    def random_linhas_relatorio(relatorio: Relatorio):
        for l in relatorio.linhas.all():
            if l.horas_extras == 0:
                l.horas_extras = random.randint(1, 44)
                l.adicional_noturno = random.randint(1, 44)
                l.save()
        relatorio.save()


    @staticmethod
    def random_new_workers(how_many):
        name_length = random.randint(2, 5)
        trabalhadores = []
        list = RandomStuff.random_worker_list(how_many, name_lenght=5)
        for d in list:
            trabalhadores.append(
                Trabalhador.objects.create(
                    nome=d[0],
                    matricula=d[1],
                    registro=d[2],
                    funcao=d[3],
                    setor=Setor.objects.get(id=1),
                    data_admissao=RandomStuff.get_random_date(datetime(1993, 1, 1), datetime.now()),
                    situacao = 'ativo'
                )
            )
        for t in trabalhadores:
            print("Criado: #%s - %s" % (t.id, t.nome))

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
        names = RandomStuff.get_names(how_many, name_lenght)
        for name in names:
            random_role = random.randint(0, len(roles) - 1)
            random_matricula = str(random.randint(8000, 19999))
            random_registro = str(random.randint(8000, 19999))
            random_date = str(random.randint(1, 28)) + "/" + str(random.randint(1, 12)) + "/" + str(
                random.randint(1993, 2020))
            worker = [name, random_matricula, random_registro, roles[random_role], random_date, 'ativo']
            workers_list.append(worker)

        return workers_list

    @staticmethod
    def get_random_date(start_date, end_date):
        diff = start_date - end_date if start_date > end_date else end_date - start_date
        random_days = random.randint(1, diff.days)
        return start_date + timedelta(days=random_days)


    @staticmethod
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

    @staticmethod
    def get_names(how_many, name_lenght=3):
        nomes = []
        with open(os.path.join(BASE_DIR, 'tests/name_list.txt')) as file:
            lines = file.readlines()
            for _ in range(how_many):
                name_lenght = random.randint(2, name_lenght)
                nome = ''
                for __ in range(name_lenght):
                    line_number = random.randint(1, len(lines) - 1)
                    nome += lines[line_number].strip('\n\0 ') + " "
                nomes.append(nome.strip())

        return nomes


class PDF:
    MAX_TABLE_LINES_RELATORIO = 34
    PDF_PATH = os.path.join(PROJECT_ROOT, 'temp/pdf.pdf')

    @staticmethod
    # std ==  SimpleDocTemplate
    def get_sdt(orientacao='r'):
        return SimpleDocTemplate(
            PDF.PDF_PATH,
            pagesize=A4,
            rightMargin=10,
            leftMargin=10,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        ) if orientacao == 'r' else SimpleDocTemplate(
            PDF.PDF_PATH,
            pagesize=(A4[1], A4[0]),
            rightMargin=10,
            leftMargin=10,
            topMargin=25 * mm,
            bottomMargin=20 * mm,
        )

    @staticmethod
    def get_flowable_line(start_x=55 * mm, width=137 * mm):
        d = Drawing(width, 1)
        d.add(Line(start_x, 0, width, 0))
        return


    @staticmethod
    def create_aviso_pdf(obj):
        doc = PDF.get_sdt(orientacao=obj['orientacao'])
        flowables = []
        img_path = ''
        if obj['tipo'] == 'alerta':
            img_path = os.path.join(BASE_DIR, 'scss/alerta.png')
        elif obj['tipo'] == 'info':
            img_path = os.path.join(BASE_DIR, 'scss/info.png')
        elif obj['tipo'] == 'urgencia':
            img_path = os.path.join(BASE_DIR, 'scss/urgencia.png')
        elif obj['tipo'] == 'proibicao':
            img_path = os.path.join(BASE_DIR, 'scss/proibicao.png')

        color = None
        if obj['orientacao'] == 'p':
            w = 70
            h = w
            font_size_titulo = 40
            font_size_conteudo = 30
            font_size_observacoes = 20
            space_before = 10

        else:
            w = 50
            h = w
            font_size_titulo = 30
            font_size_conteudo = 20
            font_size_observacoes = 15
            space_before = 32*mm


        if obj['tipo'] == 'info':
            color = Color(0, 0, 0.7, 0.8)
        elif obj['tipo'] == 'alerta':
            color = Color(0.3, 0.3, 0, 0.8)
        elif obj['tipo'] == 'urgencia':
            color = Color(0.6, 0.2, 0, 0.8)
        else:
            color = Color(1.00, 0, 0, 0.8)

        style = ParagraphStyle(name='titulo', alignment=TA_CENTER, fontSize=font_size_titulo, textColor=color, bold=True, spaceBefore=space_before,  spaceAfter=10*mm)
        style_c = ParagraphStyle(name='conteudo', alignment=TA_CENTER, leading=15*mm, fontSize=font_size_conteudo, spaceBefore=40*mm, spaceAfter=15 * mm,)
        style_r = ParagraphStyle(name='right', alignment=TA_RIGHT, leading=8*mm, fontSize=font_size_observacoes, spaceBefore=40*mm, spaceAfter=15 * mm,)

        flowables.append(
            Paragraph(
                '''<img src="%s" width="%d" height="%d" valign="sub"/><h1> - <u>%s</u> - <h1><img src="%s" width="%d" 
                height="%d" valign="sub"/>''' % (img_path, w, h,  obj['titulo'].upper(), img_path, w, h),
                style
            )
        )

        flowables.append(
            Paragraph(
             "%s" % obj['conteudo'].upper(),
                style_c
            )
        )
        if obj['observacoes']:
            flowables.append(
                Paragraph(
                    "%s" % obj['observacoes'],
                    style_r
                )
            )

        doc.build(flowables,
                  onFirstPage=PDF.papel_timbrado if obj['orientacao'] == 'r' else PDF.papel_timbrado_paisagem,
                  onLaterPages=PDF.papel_timbrado if obj['orientacao'] == 'r' else PDF.papel_timbrado_paisagem
        )



    @staticmethod
    def create_relacao_abono_pdf(obj):
        doc = PDF.get_sdt()
        data = datetime.now().date()
        flowables = []
        style = ParagraphStyle(name='titulo', alignment=TA_CENTER, fontSize=25, spaceAfter=5*mm)
        style_c = ParagraphStyle(name='sub_titulo', alignment=TA_CENTER, fontSize=13, spaceAfter=10 * mm)
        style_r = ParagraphStyle(name='right', alignment=TA_RIGHT, fontSize=12, spaceAfter=15*mm)

        flowables.append(Paragraph('<h1>RELAÇÃO DE ABONADAS<h1>', style))
        flowables.append(Paragraph('Setor: Transporte', style=style_c))
        flowables.append(
            PDF.get_flowable_line()
        )
        table_data, label = PDF.get_table_data(
            'De_%s_à_%s' % (
                obj.data_inicio.strftime('%d/%m/%Y'), 
                obj.data_termino.strftime('%d/%m/%Y'),
            ), 
            obj.abonos.all()
        )
        if table_data:
            flowables = PDF.build_table(table_data, label, flowables)

        flowables.append(PDF.get_flowable_line())

        flowables.append(Paragraph("Ilha Solteira, %d de %s de %s" % (data.day, RandomStuff.mes_escrito(data.month), data.year), style=style_r))

        flowables = PDF.assinatura_de("Sebastião Arosti", flowables=flowables, legenda="Chefe do Departamento de Transporte")
        doc.build(flowables, onFirstPage=PDF.papel_timbrado, onLaterPages=PDF.papel_timbrado)


    @staticmethod
    def create_trabalhadores_pdf(obj):
        doc = PDF.get_sdt()

        flowables = []
        style = ParagraphStyle(name='titulo', alignment=TA_CENTER, fontSize=15, spaceAfter=5 * mm)

        flowables.append(Paragraph('<h1> T R A B A L H A D O R E S </h1>', style))
        flowables.append(
            PDF.get_flowable_line()
        )

        table_data, label = PDF.get_table_data('trabalhadores', obj['trabalhadores'])
        if table_data:
            flowables = PDF.build_table(table_data, label, flowables)

        flowables.append(PDF.get_flowable_line())
        doc.build(flowables, onFirstPage=PDF.papel_timbrado, onLaterPages=PDF.papel_timbrado)



    @staticmethod
    def create_setores_pdf(obj):
        doc = PDF.get_sdt()

        flowables = []
        style = ParagraphStyle(name='titulo', alignment=TA_CENTER, fontSize=15, spaceAfter=5 * mm)

        flowables.append(Paragraph('<h1>S E C R E T A R I A S</h1>', style))
        flowables.append(
            PDF.get_flowable_line()
        )

        for k, v in obj['setor_dict'].items():
            table_data, label = PDF.get_table_data(k, v)
            if table_data:
                flowables = PDF.build_table(table_data, label, flowables)

        flowables.append(PDF.get_flowable_line())
        doc.build(flowables, onFirstPage=PDF.papel_timbrado, onLaterPages=PDF.papel_timbrado)

    @staticmethod
    def create_licencas_pdf(obj):
        doc = PDF.get_sdt()

        style = ParagraphStyle(name='titulo', alignment=TA_CENTER, fontSize=15, spaceAfter=5 * mm)
        flowables = []

        flowables.append(Paragraph('<h1> L I C E N Ç A S  -  P R Ê M I O </h1>', style))
        flowables.append(
            PDF.get_flowable_line()
        )

        for key, value in obj.items():
            table_data, label = PDF.get_table_data(key, value)
            if table_data:
                flowables = PDF.build_table(table_data, label, flowables)

        flowables.append(PDF.get_flowable_line())
        doc.build(flowables, onFirstPage=PDF.papel_timbrado, onLaterPages=PDF.papel_timbrado)

    @staticmethod
    def create_ferias_gerais_pdf(obj):
        doc = PDF.get_sdt()

        style = ParagraphStyle(name='titulo', alignment=TA_CENTER, fontSize=15, spaceAfter=5 * mm)
        flowables = []

        flowables.append(Paragraph('<h1> F  É  R  I  A  S  </h1>', style))
        flowables.append(
            PDF.get_flowable_line()
        )

        for key, value in obj.items():
            table_data, label = PDF.get_table_data(key, value)
            if table_data:
                flowables = PDF.build_table(table_data, label, flowables)

        flowables.append(PDF.get_flowable_line())

        doc.build(flowables, onFirstPage=PDF.papel_timbrado, onLaterPages=PDF.papel_timbrado)

    @staticmethod
    def build_table(table_data, label, flowables, space_after=None, space_before=None):
        if table_data:
            if label:
                flowables.append(
                    Paragraph(
                        label,
                        style=ParagraphStyle(
                            name='table_title',
                            alignment=TA_CENTER,
                            fontsize=12,
                            bold=True,
                            spaceBefore=5 * mm,
                            spaceAfter=5 * mm
                        )
                    )
                )
            flowables.append(
                Table(
                    table_data,
                    style=PDF.get_table_style(len(table_data)),
                    spaceAfter=15 * mm if not space_after else space_after,
                    spaceBefore=(10 * mm if not label else mm))) if not space_before else space_before

        return flowables

    @staticmethod
    def papel_timbrado(canvas, doc):
        PDF.draw_footer(canvas)
        PDF.draw_header(canvas)

    @staticmethod
    def papel_timbrado_paisagem(canvas, doc):
        PDF.draw_header_landscape(canvas)
        PDF.draw_footer_landscape(canvas)

    @staticmethod
    def header_duplo(canvas, doc):
        PDF.draw_header(canvas, double_page=True)

    @staticmethod
    def create_abonos_pdf(obj):

        doc = PDF.get_sdt()

        style = ParagraphStyle(name='titulo', alignment=TA_CENTER, fontSize=15, spaceAfter=5 * mm)
        flowables = []
        flowables.append(Paragraph('<h1> A  B  O  N  O  S  </h1>', style))

        flowables.append(PDF.get_flowable_line())

        for key, value in obj.items():
            table_data, label = PDF.get_table_data(key, value)
            flowables = PDF.build_table(table_data, label, flowables)

        flowables.append(PDF.get_flowable_line())

        doc.build(flowables, onFirstPage=PDF.papel_timbrado, onLaterPages=PDF.papel_timbrado)

    @staticmethod
    def create_search_pdf(dados: dict):
        hoje = datetime.now()

        doc = PDF.get_sdt()
        flowables = []

        style1 = ParagraphStyle(name='titulo', alignment=TA_CENTER, fontSize=15, spaceAfter=1 * mm)
        style2 = ParagraphStyle(name='query', alignment=TA_RIGHT, fontSize=8.5, spaceAfter=1 * mm)
        style3 = ParagraphStyle(name='horario', alignment=TA_RIGHT, fontSize=6, spaceAfter=5 * mm)
        flowables.append(Paragraph('<h1> P E S Q U I S A </h1>', style1))
        flowables.append(Paragraph('<small>termo: %s</small>' % dados['query'], style2))
        flowables.append(Paragraph('<small><i>%s</i></small>' % hoje.strftime("%d/%m/%Y %H:%M:%S"), style3))

        for k, v in dados.items():
            try:
                if v.count():
                    table_data, text = PDF.get_table_data(k, v)
                    flowables = PDF.build_table(table_data, text, flowables)
                    flowables.append(PDF.get_flowable_line())
            except Exception as e:
                print('-' * 50)
                print("label: %s - >" % k, e)
                print('-' * 50)
                pass

        doc.build(flowables, onFirstPage=PDF.papel_timbrado, onLaterPages=PDF.papel_timbrado)

    @staticmethod
    def get_table_data(key, value):
        if type(value) is QuerySet:
            if value.count() > 0:
                text = ''
                columns_data = []
                table_data = []
                palavras = key.split("_")
                if len(palavras) > 2:
                    for palavra in palavras:
                        text += palavra + " "
                if len(palavras) == 2:
                    palavras[0] = palavras[0].title()
                    palavras[1] = palavras[1].title()
                    text = palavras[0] + " " + palavras[1]
                if len(palavras) == 3:
                    palavras[0] = palavras[0].title()
                    palavras[1] = palavras[1].title()
                    palavras[2] = palavras[2].title()
                    text = palavras[0] + " " + palavras[1] + " " + palavras[2]
                elif len(palavras) == 1:
                    palavras[0] = palavras[0].title()
                    text = palavras[0]

                text = text.replace("Ferias", "Férias")
                text = text.replace("Relacao", "Relação de")
                text = text.strip()

                if type(value[0]) == Abono:
                    columns_data.append("Servidor")
                    columns_data.append("Expediente")
                    columns_data.append("Pedido")
                    columns_data.append("Fruido em")
                elif type(value[0]) == Trabalhador:
                    columns_data.append("Nome")
                    columns_data.append("Matrícula")
                    columns_data.append("Secretaria")
                    columns_data.append("Função")

                elif type(value[0]) == Setor:
                    columns_data.append("Nome")
                    columns_data.append("Qtd. servidores")

                elif type(value[0]) == LinhaRelatorio and not key == 'horas':
                    columns_data.append(('Servidor'))
                    columns_data.append(('Registro'))
                    columns_data.append(('Horas Extras'))
                    columns_data.append(('Adc. Noturno'))
                    columns_data.append(('Faltas'))
                    columns_data.append(('Faltas: datas'))

                elif type(value[0]) == LinhaRelatorio and key == 'horas':
                    columns_data.append(('Ref.'))
                    columns_data.append(('Horas Extras'))
                    columns_data.append(('Adc. Noturno'))
                    columns_data.append(('Faltas'))


                else:
                    columns_data.append("Servidor")
                    columns_data.append("Pedido")
                    columns_data.append("Saída")
                    columns_data.append("Retorno")

                table_data.append(columns_data)
                columns_data = []

                if type(value[0]) == LinhaRelatorio and not key == 'horas':
                    for linha in value:
                        if linha.horas_extras > 0.0 or linha.adicional_noturno > 0.0 or linha.faltas > 0:
                            columns_data.append(linha.trabalhador.nome)
                            columns_data.append(linha.trabalhador.registro)
                            columns_data.append(linha.horas_extras)
                            columns_data.append(("%.1f" % linha.adicional_noturno) if linha.adicional_noturno > 0 else "0")
                            columns_data.append(linha.faltas)
                            columns_data.append('-')
                            table_data.append(columns_data)
                            columns_data = []

                elif key == 'horas':
                    for linha in value:
                        if linha.horas_extras > 0.0 or linha.adicional_noturno > 0.0 or linha.faltas > 0:
                            r = Relatorio.objects.get(linhas=linha)
                            columns_data.append("%d/%d" % (r.mes, r.ano))
                            columns_data.append(linha.horas_extras)
                            columns_data.append(linha.adicional_noturno)
                            columns_data.append(linha.faltas)
                            table_data.append(columns_data)
                            columns_data = []

                else:
                    print("Value: ", value)
                    for obj in value:
                        if type(obj) == Abono:

                            columns_data.append("%s" % obj.trabalhador.nome)
                            columns_data.append("%s" % obj.trabalhador.expediente)
                            columns_data.append("%s" % (obj.criado_em.strftime("%d/%m/%Y")))
                            columns_data.append("%s" % (obj.data.strftime("%d/%m/%Y")))

                        elif type(obj) == Trabalhador:
                            columns_data.append('%s' % obj.nome)
                            columns_data.append("%s" % obj.matricula)
                            columns_data.append("%s" % obj.setor.nome)
                            columns_data.append("%s" % obj.funcao)

                        elif type(obj) == Setor:
                            columns_data.append("%s" % obj.nome)
                            columns_data.append("%s" % obj.trabalhador_set.count())

                        else:
                            columns_data.append("%s" % obj.trabalhador.nome)
                            columns_data.append("%s" % (obj.criado_em.strftime("%d/%m/%Y")))
                            columns_data.append("%s" % (obj.data_inicio.strftime("%d/%m/%Y")))
                            columns_data.append("%s" % (obj.data_termino.strftime("%d/%m/%Y")))

                        table_data.append(columns_data)
                        columns_data = []

                return table_data, text

        return None, None

    @staticmethod
    def table_fits_in_page(lines_qtt, y):
        return y > (50 * mm) or lines_qtt * (6 * mm) <= (y - (30 * mm))

    @staticmethod
    def create_setor_historico_pdf(dados: dict):
        doc = PDF.get_sdt()

        style = ParagraphStyle(name='titulo', alignment=TA_CENTER, fontSize=15, spaceAfter=5 * mm)
        style_lbl = ParagraphStyle(name='legenda', alignment=TA_CENTER, fontSize=11, spaceAfter=2*mm)
        flowables = []

        flowables.append(Paragraph('<h1> %s </h1>' % dados['setor'].nome.upper(), style))
        flowables.append(
            PDF.get_flowable_line()
        )

        for key, value in dados.items():
            table_data, label = PDF.get_table_data(key, value)
            if table_data:
                flowables = PDF.build_table(table_data, label, flowables)

        flowables.append(PDF.get_flowable_line())

        doc.build(flowables, onFirstPage=PDF.papel_timbrado, onLaterPages=PDF.papel_timbrado)

    @staticmethod
    def create_trabalhador_historico_pdf(dados: dict):
        doc = PDF.get_sdt()
        flowables = []

        style1 = ParagraphStyle(name='titulo', alignment=TA_CENTER, fontSize=15, spaceAfter=1 * mm)
        style2 = ParagraphStyle(name='nome', alignment=TA_RIGHT, fontSize=10, spaceAfter=1 * mm)
        style3 = ParagraphStyle(name='info', alignment=TA_RIGHT, fontSize=8.5, spaceAfter=5 * mm)

        flowables.append(Paragraph('<h1> T R A B A L H A D O R  </h1>', style1))
        flowables.append(Paragraph("<b>%s</b>" % dados['trabalhador'].nome, style=style2))
        flowables.append(
            Paragraph("<i>%s - %s</i>" % (dados['trabalhador'].setor.nome, dados['trabalhador'].funcao), style=style3))
        flowables.append(
            PDF.get_flowable_line()
        )

        for key, value in dados.items():
            table_data, label = PDF.get_table_data(key, value)
            if table_data:
                if len(table_data) > 1:
                    flowables = PDF.build_table(table_data, label, flowables)

        flowables.append(PDF.get_flowable_line())

        doc.build(flowables, onFirstPage=PDF.papel_timbrado, onLaterPages=PDF.papel_timbrado)

    @staticmethod
    def draw_justificativa_block(canvas, start_y, trabalhador):

        c = canvas
        spacement = 7 * mm

        data = datetime.now().date()
        PDF.draw_line(c, 155 * mm, start_y - (2 * mm), "*favor não recortar", font_size=7)
        PDF.draw_line(c, 15 * mm, start_y, "AUTORIZAÇÃO DE HORAS EXTRAS", align=TA_CENTER, font_size=15, bold=True)
        start_y -= spacement

        columns_data = []
        table_data = []
        columns_data.append("Diretoria: %s" % trabalhador.setor.nome)
        columns_data.append("")
        columns_data.append("Setor: Transporte")
        table_data.append(columns_data)
        PDF.draw_table(c, 8 * mm, start_y, table_data, 1, tipo='justificativa')
        start_y -= spacement

        columns_data.clear()
        table_data.clear()
        columns_data.append("Data: _____/______/%s" % (data.strftime('%Y')))
        columns_data.append("Horário: _____:_____ ÁS _____:_____")
        columns_data.append("H.E.: ( _____ hs. )")
        table_data.append(columns_data)
        PDF.draw_table(c, 8 * mm, start_y, table_data, 1, tipo='justificativa')
        start_y -= spacement

        columns_data.clear()
        table_data.clear()
        columns_data.append("Servidor: %s" % (trabalhador.nome.upper()))
        columns_data.append("")
        columns_data.append("Matrícula: %s" % trabalhador.matricula)
        table_data.append(columns_data)
        PDF.draw_table(c, 8 * mm, start_y, table_data, 1, tipo='justificativa')
        start_y -= spacement

        columns_data.clear()
        table_data.clear()
        columns_data.append("Motivo:%s" % ('_' * 90))
        table_data.append(columns_data)
        PDF.draw_table(c, 8 * mm, start_y, table_data, 1, tipo='justificativa')
        start_y -= spacement

        columns_data.clear()
        table_data.clear()
        columns_data.append("%s" % ('_' * 96))
        table_data.append(columns_data)
        PDF.draw_table(c, 8 * mm, start_y, table_data, 1, tipo='justificativa')
        start_y -= spacement * 1.3

        PDF.draw_line(c, 12 * mm, start_y, "%s" % ('_' * 40), font_size=10, align=TA_CENTER)
        start_y -= spacement
        PDF.draw_line(c, 12 * mm, start_y, "Sebastião Arosti", font_size=10, align=TA_CENTER)
        start_y -= spacement / 2
        PDF.draw_line(c, 12 * mm, start_y, "Chefe do Departamento de Transporte", font_size=8, align=TA_CENTER)
        start_y -= spacement * 1.3

        return start_y

    @staticmethod
    def create_justificativa_pdf(trabalhador: Trabalhador):

        c = canvas.Canvas(os.path.join(PROJECT_ROOT, 'temp/pdf.pdf'), pagesize=A4)
        start_y = 272 * mm

        PDF.draw_header(c)
        start_y = PDF.draw_justificativa_block(c, start_y, trabalhador)
        start_y = PDF.draw_justificativa_block(c, start_y, trabalhador)
        start_y = PDF.draw_justificativa_block(c, start_y, trabalhador)
        PDF.draw_justificativa_block(c, start_y, trabalhador)

        PDF.draw_footer(c)
        c.showPage()
        c.save()

    @staticmethod
    def create_licenca_pdf(licenca: LicencaPremio):

        trabalhador = licenca.trabalhador
        c = canvas.Canvas(PDF.PDF_PATH, pagesize=A4)
        start_y = 265 * mm
        spacement = 10 * mm

        data_inicio = licenca.data_inicio.strftime("%d/%m/%Y")
        data_termino = licenca.data_termino.strftime("%d/%m/%Y")
        data = datetime.now()

        # desenhando no canvas

        PDF.draw_header(c)

        PDF.draw_line(c, 0, start_y + 10 * mm, "%d dias" % licenca.qtd_dias, align=TA_RIGHT, font_size=15)
        PDF.draw_title(c, "Requerimento de Licença Prêmio", start_y)
        start_y -= spacement * 2.5
        dias_escrito = "trinta" if licenca.qtd_dias == 30 else "quinze"
        PDF.draw_line(c, 15 * mm, start_y,
                      "Através deste, venho solicitar a Vossa Senhoria, de acordo com os artigos 121 a 124 da Lei Complementar 001/93 de 01/02/1993 e Lei Complementar121/2007, de 17/01/2007, o período de gozo da Licênça Prêmio por Assiduidade, no período de:",
                      first_line_indent=50)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, '<b>%s</b> a <b>%s</b>' % (data_inicio, data_termino), align=TA_CENTER)
        start_y -= spacement

        PDF.draw_line(c, 15 * mm, start_y, "Nesse termos, peço deferimento.")
        start_y -= spacement
        PDF.draw_line(c, 130 * mm, start_y, 'Ilha Solteira, %s de %s de %s' % (
            (str(data.day) if data.day > 9 else '0' + str(data.day)),
            RandomStuff.mes_escrito(data.month),
            str(data.year)
        )
                      )
        start_y -= spacement * 1.5
        PDF.draw_line(c, 15 * mm, start_y, "__________________________", align=TA_CENTER)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "<b>%s</b>" % trabalhador.nome, align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Matrícula: %s" % trabalhador.matricula, align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Função: %s - Secretaria: %s" % (trabalhador.funcao, trabalhador.setor.nome),
                      align=TA_CENTER, font_size=10.5)

        start_y -= spacement * 1.5
        PDF.draw_line(c, 15 * mm, start_y, "__________________________", align=TA_CENTER)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Sebastião Arosti", align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Chefe do Departamento de Transporte", align=TA_CENTER, font_size=10.5)
        start_y -= spacement * 2.5

        PDF.draw_line(c, 0, start_y + 10 * mm, "%d dias" % licenca.qtd_dias, align=TA_RIGHT, font_size=15)
        PDF.draw_title(c, "Requerimento de Licença Prêmio", start_y)
        start_y -= spacement * 2.5
        PDF.draw_line(c, 15 * mm, start_y,
                      "Através deste, venho solicitar a Vossa Senhoria, de acordo com os artigos 121 a 124 da Lei Complementar 001/93 de 01/02/1993 e Lei Complementar121/2007, de 17/01/2007, o período de gozo da Licênça Prêmio por Assiduidade, no período de:",
                      first_line_indent=50)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, '<b>%s</b> a <b>%s</b>' % (data_inicio, data_termino), align=TA_CENTER)
        start_y -= spacement
        PDF.draw_line(c, 15 * mm, start_y, "Nesse termos, peço deferimento.")
        start_y -= spacement
        PDF.draw_line(c, 130 * mm, start_y, 'Ilha Solteira, %s de %s de %s' % (
            (str(data.day) if data.day > 9 else '0' + str(data.day)),
            RandomStuff.mes_escrito(data.month),
            str(data.year)
        )
                      )
        start_y -= spacement * 1.5
        PDF.draw_line(c, 15 * mm, start_y, "__________________________", align=TA_CENTER)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "<b>%s</b>" % trabalhador.nome, align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Matrícula: %s" % trabalhador.matricula, align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Função: %s - Secretaria: %s" % (trabalhador.funcao, trabalhador.setor.nome),
                      align=TA_CENTER, font_size=10.5)

        start_y -= spacement * 1.5
        PDF.draw_line(c, 15 * mm, start_y, "__________________________", align=TA_CENTER)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Sebastião Arosti", align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Chefe do Departamento de Transporte", align=TA_CENTER, font_size=10.5)

        PDF.draw_footer(c)
        c.showPage()
        c.save()

    @staticmethod
    def create_ferias_pdf(ferias: Ferias):

        trabalhador = ferias.trabalhador
        c = canvas.Canvas(PDF.PDF_PATH, pagesize=A4)
        start_y = 260 * mm
        spacement = 10 * mm

        data_inicio = ferias.data_inicio.strftime("%d/%m/%Y")
        data_termino = ferias.data_termino.strftime("%d/%m/%Y")
        data = datetime.now()

        # desenhando no canvas

        PDF.draw_header(c)

        PDF.draw_line(c, 0, start_y + 10 * mm, "%d dias" % ferias.qtd_dias, align=TA_RIGHT, font_size=15)
        PDF.draw_title(c, "Requerimento de Férias", start_y)
        start_y -= spacement * 2.5
        dias_escrito = "trinta" if ferias.qtd_dias == 30 else "quinze"
        PDF.draw_line(c, 15 * mm, start_y,
                      'Através deste, venho solicitar minhas férias de %d(%s) dias de fruição, com início no dia <b>%s</b> e término no dia <b>%s</b>' % (
                          ferias.qtd_dias, dias_escrito, data_inicio, data_termino), first_line_indent=50)
        start_y -= spacement

        PDF.draw_line(c, 15 * mm, start_y, "Nesse termos, peço deferimento.")
        start_y -= spacement
        PDF.draw_line(c, 130 * mm, start_y, 'Ilha Solteira, %s de %s de %s' % (
            (str(data.day) if data.day > 9 else '0' + str(data.day)),
            RandomStuff.mes_escrito(data.month),
            str(data.year)
        )
                      )
        start_y -= spacement * 1.5
        PDF.draw_line(c, 15 * mm, start_y, "__________________________", align=TA_CENTER)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "<b>%s</b>" % trabalhador.nome, align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Matrícula: %s" % trabalhador.matricula, align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Função: %s - Secretaria: %s" % (trabalhador.funcao, trabalhador.setor.nome),
                      align=TA_CENTER, font_size=10.5)

        start_y -= spacement * 1.5
        PDF.draw_line(c, 15 * mm, start_y, "__________________________", align=TA_CENTER)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Rodrigo Rodrigues da Silva Dias", align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Diretor do Departamento de Transporte", align=TA_CENTER, font_size=10.5)
        start_y -= spacement * 2.5

        PDF.draw_line(c, 0, start_y + 10 * mm, "%d dias" % ferias.qtd_dias, align=TA_RIGHT, font_size=15)
        PDF.draw_title(c, "Requerimento de Férias", start_y)
        start_y -= spacement * 2.5
        PDF.draw_line(c, 15 * mm, start_y,
                      'Através deste, venho solicitar minhas férias de %d(%s) dias de fruição, com início no dia <b>%s</b> e término no dia <b>%s</b>' % (
                          ferias.qtd_dias, dias_escrito, data_inicio, data_termino), first_line_indent=50)
        start_y -= spacement
        PDF.draw_line(c, 15 * mm, start_y, "Nesse termos, peço deferimento.")
        start_y -= spacement
        PDF.draw_line(c, 130 * mm, start_y, 'Ilha Solteira, %s de %s de %s' % (
            (str(data.day) if data.day > 9 else '0' + str(data.day)),
            RandomStuff.mes_escrito(data.month),
            str(data.year)
        )
                      )
        start_y -= spacement * 1.5
        PDF.draw_line(c, 15 * mm, start_y, "__________________________", align=TA_CENTER)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "<b>%s</b>" % trabalhador.nome, align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Matrícula: %s" % trabalhador.matricula, align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Função: %s - Secretaria: %s" % (trabalhador.funcao, trabalhador.setor.nome),
                      align=TA_CENTER, font_size=10.5)

        start_y -= spacement * 1.5
        PDF.draw_line(c, 15 * mm, start_y, "__________________________", align=TA_CENTER)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Rodrigo Rodrigues da Silva Dias", align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Diretor do Departamento de Transporte", align=TA_CENTER, font_size=10.5)

        PDF.draw_footer(c)
        c.showPage()
        c.save()

    @staticmethod
    def create_abono_pdf(abono: Abono):

        trabalhador = abono.trabalhador
        c = canvas.Canvas(PDF.PDF_PATH, pagesize=A4)
        start_y = 260 * mm
        spacement = 10 * mm

        data = datetime.now().date()
        data_abono = abono.data.strftime("%d/%m/%Y")

        # desenhando no canvas

        PDF.draw_header(c)

        PDF.draw_title(c, "Requerimento de Abono", start_y)
        start_y -= spacement * 3
        PDF.draw_line(
            c, 
            15 * mm, start_y,
            'Através deste, venho requerer a Vossa Senhoria, conforme dispõe a Lei Complementar 001/1993 em seu capítulo IV, artigo 129, inciso IV o abono de trabalho %s, usufruindo em <strong>%s</strong> para tratar de assuntos de interesse particular.' % (
                ('de <b>1(um) dia</b>') if abono.expediente == 'integral' else ('no expediente <b>%s</b>' % (abono.expediente)),       
                data_abono
            ), 
            first_line_indent=50
        )
        start_y -= spacement

        PDF.draw_line(c, 15 * mm, start_y, "Nesse termos, peço deferimento.")
        start_y -= spacement
        PDF.draw_line(c, 130 * mm, start_y, 'Ilha Solteira, %d de %s de %d' % (
            data.day,
            RandomStuff.mes_escrito(data.month),
            data.year
        )
                      )
        start_y -= spacement * 1.5
        PDF.draw_line(c, 15 * mm, start_y, "__________________________", align=TA_CENTER)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "<b>%s</b>" % trabalhador.nome, align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Matrícula: %s" % trabalhador.matricula, align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Função: %s - Secretaria: %s" % (trabalhador.funcao, trabalhador.setor.nome),
                      align=TA_CENTER, font_size=10.5)

        start_y -= spacement * 1.5
        PDF.draw_line(c, 15 * mm, start_y, "__________________________", align=TA_CENTER)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Sebastião Arosti", align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Chefe do Departamento de Transporte", align=TA_CENTER, font_size=10.5)
        start_y -= spacement * 2

        PDF.draw_title(c, "Requerimento de Abono", start_y)
        start_y -= spacement * 3
        PDF.draw_line(
            c, 
            15 * mm, start_y,
            'Através deste, venho requerer a Vossa Senhoria, conforme dispõe a Lei Complementar 001/1993 em seu capítulo IV, artigo 129, inciso IV o abono de trabalho %s, usufruindo em <strong>%s</strong> para tratar de assuntos de interesse particular.' % (
                ('de <b>1(um) dia</b>') if abono.expediente == 'integral' else ('no expediente <b>%s</b>' % (abono.expediente)),       
                data_abono
            ), 
            first_line_indent=50
        )
        start_y -= spacement
        PDF.draw_line(c, 15 * mm, start_y, "Nesse termos, peço deferimento.")
        start_y -= spacement
        PDF.draw_line(c, 130 * mm, start_y, 'Ilha Solteira, %s de %s de %s' % (
            data.day,
            RandomStuff.mes_escrito(data.month),
            data.year
        )
                      )
        start_y -= spacement * 1.5
        PDF.draw_line(c, 15 * mm, start_y, "__________________________", align=TA_CENTER)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "<b>%s</b>" % trabalhador.nome, align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Matrícula: %s" % trabalhador.matricula, align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Função: %s - Secretaria: %s" % (trabalhador.funcao, trabalhador.setor.nome),
                      align=TA_CENTER, font_size=10.5)

        start_y -= spacement * 1.5
        PDF.draw_line(c, 15 * mm, start_y, "__________________________", align=TA_CENTER)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Sebastião Arosti", align=TA_CENTER, font_size=10.5)
        start_y -= spacement / 2
        PDF.draw_line(c, 15 * mm, start_y, "Chefe do Departamento de Transporte", align=TA_CENTER, font_size=10.5)

        PDF.draw_footer(c)
        c.showPage()
        c.save()

    @staticmethod
    def create_relatorio_pdf(relatorio, copia=False):

        doc = PDF.get_sdt()
        flowables = []
        style_primeira_linha = ParagraphStyle(name='linha', bold=True, fontSize=12, leftIndent=15 * mm, spaceAfter=2*mm, spaceBefore=5*mm)
        style_linha = ParagraphStyle(name='linha', bold=True, fontSize=12, leftIndent=15 * mm, spaceAfter=2*mm)
        style_copia = ParagraphStyle(name='copia', bold=True, fontSize=11, alignment=TA_RIGHT, spaceBefore=10 * mm)
        style_data = ParagraphStyle(name='data', alignment=TA_RIGHT, fontSize=12, rightIndent=15*mm, spaceAfter=20*mm)

        if copia:
            flowables.append(
                Paragraph(
                    "<b>-CÓPIA-</b>",
                    style_copia,
                )
            )
        else:
            style_linha.spaceBefore = 5*mm

        flowables.append(
            Paragraph(
                "Ofício:<b>%s</b>" % relatorio.num_oficio,
                style=style_primeira_linha,
            )
        )

        style_linha.spaceBefore = 0

        flowables.append(
            Paragraph(
                "Para:<b>Divisão de Recursos Humanos</b>",
                style=style_linha
            )
        )
        flowables.append(
            Paragraph(
                "Ref.: <b>Relatório Mensal de Horas Extras ~ %s/%d</b>" % (RandomStuff.mes_escrito(relatorio.mes), relatorio.ano),
                style=style_linha
            )
        )
        flowables.append(
            Paragraph(
                "Secretaria: <b>%s</b>" % relatorio.setor.nome,
                style=style_linha
            )
        )
        flowables.append(
            Paragraph(
                "Setor: <b>Transporte</b>",
                style=style_linha
            )
        )

        table_data, label = PDF.get_table_data('relatorio', relatorio.linhas.all())
        flowables = PDF.build_table(table_data, None, flowables)
        data = relatorio.data_fechamento if relatorio.data_fechamento else datetime.now()

        flowables.append(Paragraph("Ilha Solteira, %d de %s de %s" % (data.day, RandomStuff.mes_escrito(data.month), data.year), style=style_data))

        flowables = PDF.assinatura_de("<b>Rodrigo Rodrigues da Silva Dias</b>", flowables,
                                      legenda="Diretor do Departamento de Transporte")
        flowables = PDF.assinatura_de("<b>Assinatura do(a) Secretário(a)</b>", flowables,
                                      legenda="Secretaria de %s" % relatorio.setor.nome.title())
        doc.build(flowables, onFirstPage=PDF.papel_timbrado, onLaterPages=PDF.papel_timbrado)

    @staticmethod
    def draw_header(canvas, double_page=None):
        canvas.saveState()
        x, y, w, h = [5*mm, 277*mm, 193*mm, 15*mm]

        canvas.drawInlineImage(
            os.path.join(BASE_DIR, 'tests/header.jpeg'),
            x,
            y,
            w,
            h
        )
        if double_page:
            canvas.drawInlineImage(
                os.path.join(BASE_DIR, 'tests/header.jpeg'),
                x,
                (y - (10*mm)) / 2,
                w,
                h,
            )

        canvas.restoreState()

    @staticmethod
    def draw_header_landscape(canvas, double_page=None):
        canvas.saveState()
        x, y, w, h = [0, 183 * mm, 288 * mm, 20 * mm]

        canvas.drawInlineImage(
            os.path.join(BASE_DIR, 'tests/header.jpeg'),
            x,
            y,
            w,
            h
        )
        if double_page:
            canvas.drawInlineImage(
                os.path.join(BASE_DIR, 'tests/header.jpeg'),
                x,
                (y - (10 * mm)) / 2,
                w,
                h,
            )
        canvas.restoreState()

    @staticmethod
    def draw_footer(canvas):
        canvas.saveState()
        canvas.drawInlineImage(
            os.path.join(BASE_DIR, 'tests/footer.jpeg'),
            8*mm,
            7 * mm,
            193 * mm,
            15 * mm
        )
        canvas.restoreState()

    @staticmethod
    def draw_footer_landscape(canvas):
        canvas.saveState()
        canvas.drawInlineImage(
            os.path.join(BASE_DIR, 'tests/footer.jpeg'),
            5*mm,
            7 * mm,
            288 * mm,
            20 * mm
        )
        canvas.restoreState()


    @staticmethod
    def draw_title(canvas, text, y):
        canvas.saveState()
        sample_style_sheet = getSampleStyleSheet()
        style = sample_style_sheet['h1']
        style.fontName = "Helvetica-Bold"
        style.fontSize = 25
        style.alignment = TA_CENTER
        p = Paragraph(text.upper(), style)
        p.wrap(210 * mm, 25)
        p.drawOn(canvas, 2, y)
        canvas.restoreState()

    @staticmethod
    def draw_thats_a_copy(canvas):
        canvas.saveState()
        sample_style_sheet = getSampleStyleSheet()
        style = sample_style_sheet['h5']
        style.fontName = "Helvetica-Bold"
        style.fontSize = 12
        p = Paragraph('-CÓPIA', style)
        p.wrap(297 * mm, 25 * mm)
        p.drawOn(canvas, 175 * mm, 265 * mm)
        canvas.restoreState()

    @staticmethod
    def draw_line(canvas, x, y, text, bold=False, align=TA_JUSTIFY, font_size=12, first_line_indent=0):

        canvas.saveState()
        sample_style_sheet = getSampleStyleSheet()
        style = sample_style_sheet['BodyText']
        style.fontName = "Helvetica-Bold" if bold else "Helvetica"
        style.fontSize = font_size
        style.alignment = align
        style.firstLineIndent = first_line_indent
        p = Paragraph(text, style)
        p.wrap(180 * mm, 100)
        p.drawOn(canvas, x, y)
        canvas.restoreState()

    @staticmethod
    def draw_table(canvas, x, y, data, lines_qtt, tipo='relatorio'):

        canvas.saveState()
        t = None
        X_SPACE = 193 * mm

        if tipo != 'justificativa':
            if tipo == 'trabalhador_historico':
                t = Table(data, style=PDF.get_table_style(len(data)))
            else:
                t = Table(data, style=PDF.get_table_style(lines_qtt))
            t.wrap(200 * mm, 10 * mm * lines_qtt)
        else:
            t = Table(data, colWidths=80 * mm)
            t.wrap(190 * mm, 10 * mm)
        if t:
            t.drawOn(canvas, x, y)
        canvas.restoreState()

    @staticmethod
    def get_table_style(lines_qtt):

        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0, 0.2, 0.5, alpha=0.7)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), "CENTER"),
            ('FONTSIZE', (0, 0), (-1, 0), 11.5),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]

        if lines_qtt > 15:
            table_style.append(('FONTSIZE', (0, 0), (-1, 0), 10))
            table_style.append(('FONTSIZE', (0, 0), (-1, -1), 9.5))

        return TableStyle(table_style)

    @staticmethod
    def assinatura_de(quem, flowables, legenda=None, sub_legenda=None):
        style_traco = ParagraphStyle(name='traco', alignment=TA_CENTER)
        style = ParagraphStyle(name='assinatura', alignment=TA_CENTER, fontsize=12,
                               spaceAfter=mm if legenda else 15 * mm)
        style_leg = ParagraphStyle(name='assinatura', alignment=TA_CENTER, fontsize=10,
                                   spaceAfter=mm if sub_legenda else 15 * mm)
        style_sub_leg = ParagraphStyle(name='assinatura', alignment=TA_CENTER, fontsize=9, spaceAfter=15 * mm)
        traco_texto = "____________________________________"
        flowables.append(
            Paragraph(
                traco_texto,
                style_traco,
            )
        )
        flowables.append(
            Paragraph(
                quem,
                style,
            )
        )
        if legenda:
            flowables.append(
                Paragraph(
                    legenda,
                    style_leg,
                )
            )
            if sub_legenda:
                flowables.append(
                    Paragraph(
                        sub_legenda,
                        style_sub_leg,
                    )
                )
        return flowables

    @staticmethod
    def create_atestado_trabalho(obj):
        doc = PDF.get_sdt()

        style_titulo = ParagraphStyle(name='titulo', alignment=TA_CENTER, fontSize=25, spaceAfter=45 * mm)
        style_linha = ParagraphStyle(name='linha', alignment=TA_JUSTIFY, fontSize=15, spaceAfter=25 * mm, leading=10*mm, spaceShrinkage=0.2, firstLineIndent=10*mm, rightIndent=10*mm, leftIndent=10*mm)
        style_data = ParagraphStyle(name='data', alignment=TA_RIGHT, fontSize=15, spaceAfter=85*mm, rightIndent=10*mm)
        flowables = []
        flowables.append(Paragraph('<h1> ATESTADO DE TRABALHO</h1>', style_titulo))

        flowables.append(PDF.get_flowable_line())

        flowables.append(
            Paragraph(
                "Declaramos para os devidos fins que o(a) Sr.(a) %s, %s, inscrito(a) no CPF sob o nº %s, no RG nº %s, "
                "e portador da CTPS nº %s - Série %s, é funcionário(a) desta empresa, na função de %s, laborando das "
                "7:30 ás 12:00 e das 13:30 ás 17:00, de segunda á sexta-feira." % (
                    obj['trabalhador'].nome,
                    obj['trabalhador'].funcao,
                    obj['cpf'],
                    obj['rg'],
                    obj['ctps'],
                    obj['ctps_serie'],
                    obj['trabalhador'].funcao,
                ),
                style=style_linha
            )
        )
        data = datetime.now()
        flowables.append(
            Paragraph(
                "Ilha Solteira, %d de %s de %d." % (data.day, RandomStuff.mes_escrito(data.month), data.year),
                style=style_data
            )
        )

        flowables = PDF.assinatura_de("Sebastião Arosti",flowables, legenda="Chefe do Departamento de Transporte")

        doc.build(flowables, onFirstPage=PDF.papel_timbrado, onLaterPages=PDF.papel_timbrado)


    @staticmethod
    def create_sexta_parte_pdf(obj):
        doc = PDF.get_sdt()

        style_titulo = ParagraphStyle(name='titulo', alignment=TA_CENTER, fontSize=25, spaceAfter=45 * mm)
        style_linha = ParagraphStyle(name='linha', alignment=TA_JUSTIFY, fontSize=15, spaceAfter=25 * mm, leading=10*mm, spaceShrinkage=0.2, firstLineIndent=10*mm, rightIndent=10*mm, leftIndent=10*mm)
        style_data = ParagraphStyle(name='data', alignment=TA_RIGHT, fontSize=15, spaceAfter=85*mm, rightIndent=10*mm)
        flowables = []
        flowables.append(Paragraph('<h1>REQUERIMENTO SEXTA PARTE</h1>', style_titulo))

        flowables.append(
            Paragraph(
                "Eu, %s, RG: %s, CPF: %s, Matrícula: %s, servidor efetivo(a) no cargo de "
                "%s, venho mui respeitosamente solicitar a Vossa Senhoria, conceder-me Adicional "
                " Sexta Parte, benefício previsto no Art. 92 da Lei Municipal Complementar 001/93, " 
                "de 1 de fevereiro de 1993, visto ter atingido 20(vinte) anos de serviços prestados ao "
                "município, desde %s." % (
                    obj['trabalhador'].nome,
                    obj['rg'],
                    obj['cpf'],
                    obj['trabalhador'].matricula,
                    obj['trabalhador'].funcao,
                    obj['trabalhador'].data_admissao.strftime("%d/%m/%Y"),
                ),
                style=style_linha
            )
        )
        data = datetime.now()
        flowables.append(
            Paragraph(
                "Ilha Solteira, %d de %s de %d." % (data.day, RandomStuff.mes_escrito(data.month), data.year),
                style=style_data
            )
        )

        flowables = PDF.assinatura_de("%s" % obj['trabalhador'].nome, flowables, legenda="%s" % obj['trabalhador'].funcao)

        doc.build(flowables, onFirstPage=PDF.papel_timbrado, onLaterPages=PDF.papel_timbrado)

    @staticmethod
    def create_materiais_block(flowables):
        style_linha = ParagraphStyle(name='linha', alignment=TA_JUSTIFY, fontSize=12, spaceAfter=2 * mm)
        style_titulo = ParagraphStyle(name='titulo', alignment=TA_CENTER, fontSize=25, spaceAfter=10*mm)
        flowables.append(
            Paragraph(
                "<b>REQUISIÇÃO DE MATERIAIS</b>",
                style_titulo
            )
        )

        flowables.append(
            Paragraph(
                "SETOR REQUISITANTE:" + "_" * 62,
                style_linha
            )
        )

        flowables.append(
            Paragraph(
                "APLICAÇÃO DE MATERIAIS:" + "_" * 59,
                style_linha
            )
        )

        table_data = [
            ['CÓDIGO', "QUANT.", "UN.", "ESPECIFICAÇÃO", "OBS."],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' '],
        ]
        table_style = PDF.get_table_style(len(table_data))
        table_style.add('BOTTOMPADDING', (0, 0), (-1, -1), 4)
        table_style.add('TOPPADDING', (0, 0), (-1, -1), 4)

        flowables.append(
            Table(
                table_data,
                style=table_style,
                colWidths=[35 * mm, 15 * mm, 10 * mm, 95 * mm, 40 * mm],
                spaceAfter=5*mm

            )
        )
        table_data = [
            ["________/________/________", "________/________/________", "________/________/________"]
        ]
        flowables.append(
            Table(
                table_data,
                style=TableStyle(
                    [
                        ('ALIGN', (0, 0), (-1, -1), "CENTER"),
                        ('FONTSIZE', (0, 0), (-1, 0), 11.5),
                    ],
                ),
                colWidths=[A4[0] / 3, A4[0] / 3, A4[0] / 3],
                spaceAfter=5*mm,
            )
        )
        table_data = [
            ["______________________", "______________________", "______________________"],
            ['REQUISITANTE', 'APROVAÇÃO DO SETOR', 'ALMOXARIFADO'],
            ['(AUTORIZADO)', '(RESPONSÁVEL)', '(ATENDIDO)']
        ]
        flowables.append(
            Table(
                table_data,
                style=TableStyle(
                    [
                        ('ALIGN', (0, 0), (-1, -1), "CENTER"),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('FONTSIZE', (0, 2), (-1, -1), 7),
                    ],
                ),
                colWidths=[A4[0] / 3, A4[0] / 3, A4[0] / 3],
                spaceAfter=27 * mm,
            )
        )


    @staticmethod
    def create_materiais_pdf():
        doc = SimpleDocTemplate(
            PDF.PDF_PATH,
            pagesize=A4,
            rightMargin=10,
            leftMargin=10,
            topMargin=15 * mm,
            bottomMargin=5 * mm,

        )
        flowables = []

        PDF.create_materiais_block(flowables)
        PDF.create_materiais_block(flowables)

        doc.build(flowables, onFirstPage=PDF.header_duplo, onLaterPages=PDF.header_duplo)


class PDFFactory(PDF):

    @staticmethod
    def get_atestado_trabalho(obj: dict):
        if obj:
            PDFFactory.create_atestado_trabalho(obj)

    @staticmethod
    def get_setores_pdf(obj: dict):
        if obj:
            PDFFactory.create_setores_pdf(obj)

    @staticmethod
    def get_trabalhadores_pdf(obj: dict):
        if obj:
            PDFFactory.create_trabalhadores_pdf(obj)

    @staticmethod
    def get_trabalhador_historico_pdf(dados: dict):
        if dados:
            PDFFactory.create_trabalhador_historico_pdf(dados)

    @staticmethod
    def get_justificativa_pdf(trabalhador: Trabalhador):
        if trabalhador:
            PDFFactory.create_justificativa_pdf(trabalhador)

    @staticmethod
    def get_abono_pdf(abono: Abono):
        if abono:
            PDFFactory.create_abono_pdf(abono)

    @staticmethod
    def get_ferias_pdf(ferias: Ferias):
        if ferias:
            PDFFactory.create_ferias_pdf(ferias)

    @staticmethod
    def get_licenca_pdf(licenca: LicencaPremio):
        if licenca:
            PDFFactory.create_licenca_pdf(licenca)

    @staticmethod
    def get_relatorio_pdf(relatorio: Relatorio, copia=False):
        PDFFactory.create_relatorio_pdf(
            relatorio,
            copia=copia
        )

        print("PDF do relatório do meŝ de %s, com %d linhas, foi criado em ../feriapp/temp/pdf.pdf" % (
            RandomStuff.mes_escrito(relatorio.mes), relatorio.linhas.count()))

    @staticmethod
    def get_setor_historico_pdf(obj: dict):
        if obj:
            PDFFactory.create_setor_historico_pdf(obj)

    @staticmethod
    def get_search_pdf(obj: dict):
        if obj:
            PDFFactory.create_search_pdf(obj)

    @staticmethod
    def get_abonos_pdf(obj: dict):
        if obj:
            PDFFactory.create_abonos_pdf(obj)

    @staticmethod
    def get_ferias_gerais_pdf(obj: dict):
        if obj:
            PDFFactory.create_ferias_gerais_pdf(obj)

    @staticmethod
    def get_licencas_pdf(obj: dict):
        if obj:
            PDFFactory.create_licencas_pdf(obj)

    @staticmethod
    def get_relacao_abono_pdf(obj):
        if obj:
            PDFFactory.create_relacao_abono_pdf(obj)

    @staticmethod
    def get_sexta_parte_pdf(obj):
        if obj:
            PDFFactory.create_sexta_parte_pdf(obj)

    @staticmethod
    def get_materiais_pdf():
        PDFFactory.create_materiais_pdf()

    @staticmethod
    def get_aviso_pdf(obj):
        if obj:
            PDFFactory.create_aviso_pdf(obj)


'''


        text = """
        Ofício: %s\n
        Para: Divisão de Recursos Humanos\n
        Ref.: Relatório Mensal de Horas Extras  - %s/%d\n
        Secretaria: %s\n
        Setor: Transporte
        """ % (num_oficio, mes_escrito, ano, setor)

'''
