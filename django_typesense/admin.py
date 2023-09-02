from django.contrib import admin

from django_typesense.models import TypesenseAPIKey


@admin.register(TypesenseAPIKey)
class TypesenseAPIKeyAdmin(admin.ModelAdmin):
    pass
