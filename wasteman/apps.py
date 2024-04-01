from django.apps import AppConfig


class WastemanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wasteman'

    def ready(self):
        import wasteman.signals
