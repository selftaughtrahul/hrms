from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources.
    Required for rendering images (like the company logo) in the PDF.
    """
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.BASE_DIR, 'static', uri.replace(settings.STATIC_URL, ""))
    else:
        return uri

    # Make sure that file exists
    if not os.path.isfile(path):
        raise Exception(f'Media URI must start with {settings.MEDIA_URL} or {settings.STATIC_URL}')
    return path

def render_to_pdf(template_src, context_dict={}):
    """
    Renders a Django HTML template into a PDF document using xhtml2pdf.
    Returns an HttpResponse with PDF content, or None if linking failed.
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    
    result = BytesIO()
    
    # Generate PDF
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("utf-8")), 
        result,
        link_callback=link_callback
    )
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
