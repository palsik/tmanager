from django.apps import AppConfig

from apps import home


class palstekAiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.home'

    ## call the signal
    def ready(self):
        import apps.home.signals
