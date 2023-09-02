from django.apps import AppConfig


class DjangoTypesenseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_typesense"

    def ready(self) -> None:
        import django_typesense.signals  # noqa

        return super().ready()
