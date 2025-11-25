from django import template
from sistemas.models import Correos

register = template.Library()

@register.simple_tag
def obtener_correos():
    return Correos.objects.select_related('usuario').all()
