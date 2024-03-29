from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from app import views
from django.contrib.sitemaps.views import sitemap
from app.sitemaps import *

sitemaps = {
        "setores": SetorSitemap,
        "trabalhadores": TrabalhadorSitemap,
        "ferias": FeriasSitemap,
        "licencas": LicencaPremioSitemap,
        "abonos": AbonoSitemap
}



urlpatterns = [
    path('', views.index, name="index"),
    path('ferias/', views.ferias, name='ferias'),
    path('ferias/<ordenation>/', views.ferias, name='ferias'),
    path('licencas/', views.licenca_premio, name='licenca_premio'),
    path('licencas/<ordenation>', views.licenca_premio, name='licenca_premio'),
    path('abonos/', views.abono, name='abono'),
    path('abonos/<ordenation>/', views.abono, name='abono'),
    path('trabalhador/', views.trabalhador, name='trabalhador'),
    path("trabalhador/<int:trabalhador_id>/", views.trabalhador, name='trabalhador'),
    path("trabalhador/<int:trabalhador_id>/<ordenation>/", views.trabalhador, name='trabalhador'),
    path("setores/", views.setor, name="setor"),
    path("setores/<ordenation>/", views.setor, name="setor"),
    path("setor/", views.setor_espec, name='setor_espec'),
    path("setor/<ordenation>/", views.setor_espec, name='setor_espec'),
    path("marcar-ferias/", views.marcar_ferias, name="marcar_ferias"),
    path("marcar-licenca/", views.marcar_licenca, name="marcar_licenca"),
    path("marcar-abono/", views.marcar_abono, name="marcar_abono"),
    path("novo-setor/", views.novo_setor, name="novo_setor"),
    path("novo-trabalhador/", views.novo_trabalhador, name="novo_trabalhador"),
    path("trabalhadores/", views.trabalhadores, name='trabalhadores'),
    path("trabalhadores/<ordenation>/", views.trabalhadores, name='trabalhadores'),
    path("pesquisa/", views.pesquisa, name='pesquisa'),
    path("pesquisa/<ordenation>/", views.pesquisa, name='pesquisa'),
    path("editar-data/", views.editar_data, name='editar_data'),
    path("editar-trabalhador/", views.editar_trabalhador, name='editar_trabalhador'),
    path("editar-setor/", views.editar_setor, name='editar_setor'),
    path("excluir-setor/", views.excluir_setor, name='excluir_setor'),
    path("excluir-trabalhador/", views.excluir_trabalhador, name='excluir_trabalhador'),
    path("indeferir/", views.indeferir, name='indeferir'),
    path('entrar/', views.entrar, name='entrar'),
    path('sair/', views.sair, name='sair'),
    path('soma-justificativas/', views.soma_justificativas, name='soma_justificativas'),
    path('soma-horas/', views.soma_horas, name='soma_horas'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('autorizacao-he/', views.autorizacao, name='autorizacao'),
    path('relatorio-edicao/<int:relatorio_id>', views.relatorio_edicao, name='relatorio_edicao'),
    path('modifica-relatorio/', views.modifica_relatorio, name='modifica_relatorio'),
    path('pdf/<str:tipo>/<int:obj_id>/', views.pdf, name='pdf'),
    path('divide-linha/', views.divide_linha, name='divide_linha'),
    path('finalizar_relatorios/', views.finalizar_relatorios, name='finalizar_relatorios'),
    path('atestado/', views.atestado, name='atestado'),
    path('sexta-parte/', views.sexta_parte, name='sexta_parte'),
    path('aviso/', views.aviso, name='aviso'),
    path('conf/', views.conf, name='conf'),
    path('done/<int:pk>/', views.marcar_como_feito, name='marcar_como_feito'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
                        name='django.contrib.sitemaps.views.sitemap')

]