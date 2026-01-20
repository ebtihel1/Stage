from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'  # Le chemin Python pour l'importation
    label = 'users'      # Le nom unique utilisé pour les relations et réglages