from django.apps import AppConfig


class SistemasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sistemas'

    def ready(self):
        import sistemas.signals
