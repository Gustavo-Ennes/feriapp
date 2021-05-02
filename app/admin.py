from django.contrib import admin
from app.models import *
from myapp.seo import MyMetadatafrom 
from rollyourown.seo.admin import register_seo_admin


class TrabalhadorAdmin(admin.ModelAdmin):
    pass


class FeriasAdmin(admin.ModelAdmin):
    pass


class LicencaPremioAdmin(admin.ModelAdmin):
    pass


class AbonoAdmin(admin.ModelAdmin):
    pass


class SetorAdmin(admin.ModelAdmin):
    pass


class RelatorioAdmin(admin.ModelAdmin):
    pass


class LinhaRelatorioAdmin(admin.ModelAdmin):
    pass


class LembreteAdmin(admin.ModelAdmin):
    pass


class DiretorAdmin(admin.ModelAdmin):
    pass


class ChefeDeSetorAdmin(admin.ModelAdmin):
    pass




admin.site.register(Trabalhador, TrabalhadorAdmin)
admin.site.register(Ferias, FeriasAdmin)
admin.site.register(LicencaPremio, LicencaPremioAdmin)
admin.site.register(Abono, AbonoAdmin)
admin.site.register(Setor, SetorAdmin)
admin.site.register(Relatorio, RelatorioAdmin)
admin.site.register(LinhaRelatorio, LinhaRelatorioAdmin)
admin.site.register(Lembrete, LembreteAdmin)
admin.site.register(Diretor, DiretorAdmin)
admin.site.register(ChefeDeSetor, ChefeDeSetorAdmin)


register_seo_admin(admin.site, MyMetadata)
