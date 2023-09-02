from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TypesenseAPIAction(models.Model):
    """
    Stores a Typesense API action. This is used to
    minimize the permissions of an API key.
    """

    class Actions(models.TextChoices):
        # Documents actions
        DOCUMENTS_GET = "documents:get", _("Get Documents")
        DOCUMENTS_SEARCH = "documents:search", _("Search Documents")
        DOCUMENTS_CREATE = "documents:create", _("Create Documents")
        DOCUMENTS_UPSERT = "documents:upsert", _("Upsert Documents")
        DOCUMENTS_UPDATE = "documents:update", _("Update Documents")
        DOCUMENTS_DELETE = "documents:delete", _("Delete Documents")
        DOCUMENTS_IMPORT = "documents:import", _("Import Documents")

        # Collections actions
        COLLECTIONS_GET = "collections:get", _("Get Collections")
        COLLECTIONS_LIST = "collections:list", _("List Collections")
        COLLECTIONS_CREATE = "collections:create", _("Create Collections")
        COLLECTIONS_DELETE = "collections:delete", _("Delete Collections")

        # Aliases actions
        ALIASES_GET = "aliases:get", _("Get Aliases")
        ALIASES_LIST = "aliases:list", _("List Aliases")
        ALIASES_CREATE = "aliases:create", _("Create Aliases")
        ALIASES_DELETE = "aliases:delete", _("Delete Aliases")

        # Synonyms actions
        SYNONYMS_GET = "synonyms:get", _("Get Synonyms")
        SYNONYMS_LIST = "synonyms:list", _("List Synonyms")
        SYNONYMS_CREATE = "synonyms:create", _("Create Synonyms")
        SYNONYMS_DELETE = "synonyms:delete", _("Delete Synonyms")

        # Keys actions
        KEYS_GET = "keys:get", _("Get Keys")
        KEYS_LIST = "keys:list", _("List Keys")
        KEYS_CREATE = "keys:create", _("Create Keys")
        KEYS_DELETE = "keys:delete", _("Delete Keys")

        # Misc actions
        DEBUG_LIST = "debug:list", _("Debug Access")
        METRICS_LIST = "metrics.json:list", _("Metrics Access")

    permission = models.CharField(
        db_index=True,
        max_length=64,
        unique=True,
        choices=Actions.choices,
        help_text=_("The API permission"),
    )

    class Meta:
        verbose_name = _("Typesense API permission")
        verbose_name_plural = _("Typesense API permissions")

    def __str__(self) -> str:
        return self.get_permission_display()


class TypesenseAPIKey(models.Model):
    """
    Stores a Typesense API Key. This is used to
    authenticate the user with the Typesense server.
    Try to keep the allowed actions to a minimum.
    """

    created_on = models.DateTimeField(auto_now_add=True, help_text=_("The date and time this key was created"))

    value = models.CharField(max_length=64, unique=True, editable=False, help_text=_("The API key"))
    description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_("Description of the API key"),
    )

    actions = models.ManyToManyField(
        TypesenseAPIAction,
        blank=True,
        help_text=_("The API permissions"),
        related_name="api_keys",
    )

    collections = models.CharField(
        max_length=255, help_text=_("Comma-separated list of collections this key has access to")
    )

    # fmt: off
    expires_at_dt = models.DateTimeField(
        blank=True,
        help_text=_('The date and time at which this key expires. '
                    'Will be set to 1 year from now if left blank.'),
    )
    # fmt: on

    class Meta:
        verbose_name = _("Typesense API key")
        verbose_name_plural = _("Typesense API keys")

    @property
    def expires_at_unix(self) -> int:
        """
        Typesense expects the `expires_at` field to be a UNIX timestamp. Fair enough.
        """
        return int(self.expires_at_dt.timestamp())

    @property
    def read_only(self) -> bool:
        """
        Returns True if the API key is read-only.
        """
        return (
            self.actions.filter(
                permission__in=(
                    TypesenseAPIAction.Actions.DOCUMENTS_GET,
                    TypesenseAPIAction.Actions.DOCUMENTS_SEARCH,
                )
            ).count()
            == 2
        )

    def save(self, *args, **kwargs):
        if self._state.adding:
            if not self.expires_at_dt:
                self.expires_at_dt = timezone.now() + timezone.timedelta(days=365)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.value
