from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create Typesense indices'

    def handle(self, **options):
        pass
