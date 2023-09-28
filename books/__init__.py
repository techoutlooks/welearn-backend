from django.apps import AppConfig


class BookApp(AppConfig):
    name = 'books'

    def ready(self):
        from . import signals


default_app_config = 'books.BookApp'
