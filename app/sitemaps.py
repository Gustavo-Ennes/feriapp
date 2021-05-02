from django.contrib.sitemaps import Sitemap

from .models import *

class SetorSitemap(Sitemap):
        changefreq = "weekly"
        priority = 0.9

        def items(self):
                return Setor.objects.all()

        def lastmod(self, obj):
                return obj.modificado_em


class TrabalhadorSitemap(Sitemap):
        changefreq = "weekly"
        priority = 0.9

        def items(self):
                return Trabalhador.objects.all()

        def lastmod(self, obj):
                return obj.modificado_em


class FeriasSitemap(Sitemap):
        changefreq = "weekly"
        priority = 0.9

        def items(self):
                return Ferias.objects.all()

        def lastmod(self, obj):
                return obj.modificado_em


class LicencaPremioSitemap(Sitemap):
        changefreq = "weekly"
        priority = 0.9

        def items(self):
                return LicencaPremio.objects.all()

        def lastmod(self, obj):
                return obj.modificado_em


class AbonoSitemap(Sitemap):
        changefreq = "weekly"
        priority = 0.9

        def items(self):
                return Abono.objects.all()

        def lastmod(self, obj):
                return obj.modificado_em