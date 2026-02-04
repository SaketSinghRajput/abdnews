from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    
    def ready(self):
        """Import signals when app is ready"""
        # Signals for future auto-creation of Author profiles can be imported here
        pass
