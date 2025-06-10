from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Juego, Stock

@receiver(post_save, sender=Stock)
def update_juego_stock(sender, instance, **kwargs):
    """Actualiza el stock total del juego cuando se modifica un stock"""
    instance.juego.stock_total = instance.juego.stocks.aggregate(total=Sum('cantidad'))['total'] or 0
    instance.juego.save(update_fields=['stock_total'])