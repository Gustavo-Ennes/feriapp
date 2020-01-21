from django.contrib import admin
from app.models import *

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


admin.site.register(Trabalhador, TrabalhadorAdmin)
admin.site.register(Ferias, FeriasAdmin)
admin.site.register(LicencaPremio, LicencaPremioAdmin)
admin.site.register(Abono, AbonoAdmin)
admin.site.register(Setor, SetorAdmin)
