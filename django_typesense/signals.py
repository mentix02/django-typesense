from typing import Type

from django.conf import settings
from django.apps import AppConfig
from django.db import IntegrityError
from django.dispatch import receiver
from django.core.management.base import OutputWrapper
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save, post_migrate

from django_typesense.client import client
from django_typesense.models import TypesenseAPIKey
from django_typesense.apps import DjangoTypesenseConfig


@receiver(post_migrate)
def populate_actions(sender: AppConfig, stdout: OutputWrapper, verbosity: int, **kwargs):
    """
    Check when django_typesense is loaded and insert all the TypesenseAPIPermission
    objects according to the actions defined in the TypesenseAPIAction.Actions class.
    """

    if sender.name == DjangoTypesenseConfig.name:
        from django_typesense.models import TypesenseAPIAction

        for action in TypesenseAPIAction.Actions:  # type: ignore[attr-defined]
            permission, created = TypesenseAPIAction.objects.get_or_create(permission=action.value)

            if verbosity > 1 and created:
                stdout.write(f"Adding Typesense action {permission}")


@receiver(pre_save, sender=TypesenseAPIKey)
def sync_typesense_value_into_db(sender: Type[TypesenseAPIKey], instance: TypesenseAPIKey, **kwargs):
    """
    Makes the actual request to the Typesense server to create the API Key.
    Fetch the generated key and store it in the `value` field. Delete the
    previous key if it exists (in case of an update).
    """

    # Check if the instance is being updated
    if instance.pk or instance.value:
        # Delete the previous key. First, list all the keys
        keys = client.keys.retrieve()["keys"]
        # Then, delete the key with the value prefix
        for key in keys:
            if instance.value.startswith(key["value_prefix"]):
                idx_to_delete = key["id"]
                # Delete the key
                client.keys[idx_to_delete].delete()
                break
        else:
            # No key found, something is wrong. Most likely the key was deleted
            # manually from the Typesense dashboard OR Typesense was restarted
            # from a fresh state. We can either raise an error or continue,
            # depending on whether the setting `DJANGO_TYPESENSE_STRICT_KEY_SYNC`
            # is set to True or False. By default, it's set to False, and
            # we can just fail silently and continue with a brand-new key
            # by just requesting a new one (which Typesensee would create).
            if getattr(settings, "DJANGO_TYPESENSE_STRICT_KEY_SYNC", True):
                msg = _(
                    f"The Typesense API key {instance.value} was not found in the Typesense server. "
                    "It has either been deleted manually or Typesense was restarted from a fresh state. "
                    "Please delete the key from the primary database and create a new one."
                )
                raise IntegrityError(msg)
            else:
                instance.value = None

    # Continue with the creation of a brand-new key

    resp = client.keys.create(
        {
            "actions": instance.actions,
            "description": instance.description,
            "collections": instance.collections,
            "expires_at": instance.expires_at_unix,
        }
    )

    instance.value = resp["value"]
