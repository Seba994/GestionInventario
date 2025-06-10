"""
funciones utilitarias para el sistema de inventario
"""
from django.db.models import Sum
from .models import Stock

def calcular_stock(juego):
    """
    Calcula el stock total de un juego específico.
    """
    return Stock.objects.filter(juego=juego).aggregate(
        total=Sum('cantidad')
    )['total'] or 0
