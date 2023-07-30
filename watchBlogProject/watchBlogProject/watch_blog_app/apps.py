from django.apps import AppConfig


class WatchBlogAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'watchBlogProject.watch_blog_app'

    def ready(self):
        from . import signals
