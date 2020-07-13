from io import BytesIO, StringIO
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
import os

class Render:
    @staticmethod
    def render(path: str, params: dict, image=False):
        template = get_template(path)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)

        if image:
            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), dest=response, link_callback=Render.fetch_resources)
        else:
            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)

        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        else:
            return HttpResponse("Error Rendering PDF", status=400)

    @staticmethod
    def fetch_resources(uri, rel):
        path = os.path.join(settings.STATIC_ROOT, 'background.jpg')

        return path
