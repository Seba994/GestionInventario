from django.db.models import Sum

def calcular_stock(juego):
    from .models import Stock 
    return Stock.objects.filter(juego=juego).aggregate(
        total=Sum('cantidad')
    )['total'] or 0