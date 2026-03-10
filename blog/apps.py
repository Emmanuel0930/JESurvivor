from importlib import import_module
from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def import_models(self):
        super().import_models()
        self.models_module = import_module('blog.domain.models')