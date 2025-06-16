from django import template
from sistemas.models import AlertaStock

register = template.Library()

@register.simple_tag
def get_stock_alerts():
    return AlertaStock.objects.all().order_by('-creada_en')
