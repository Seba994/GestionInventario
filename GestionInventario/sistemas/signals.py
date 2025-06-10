from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Juego, Stock

@receiver(post_save, sender=Stock)
def update_juego_stock(sender, instance, **kwargs):
    """Actualiza el stock total del juego cuando se modifica un stock"""
    pass