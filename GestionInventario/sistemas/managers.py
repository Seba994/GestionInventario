from django.db import models

class JuegoManager(models.Manager):
    def with_stock(self):
        return self.get_queryset().annotate(
            stock_total=models.Sum('stocks__cantidad')
        )