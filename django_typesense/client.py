from typesense import Client

from django.conf import settings
from django.utils.functional import SimpleLazyObject


class LazyTypesenseClient(Client):
    """
    TypesenseClient is a lazy singleton class that provides a Typesense client
    instance. It is a singleton because we don't want to create multiple
    connections to the Typesense server.
    """

    def __init__(self):
        super().__init__(
            {
                "nodes": settings.TYPESENSE_NODES,
                "api_key": settings.TYPESENSE_ADMIN_API_KEY,
                "num_retries": getattr(settings, "TYPESENSE_NUM_RETRIES", 3),
                "retry_interval_seconds": getattr(settings, "TYPESENSE_RETRY_INTERVAL_SECONDS", 1.0),
                "connection_timeout_seconds": getattr(settings, "TYPESENSE_CONNECTION_TIMEOUT_SECONDS", 3.0),
                "healthcheck_interval_seconds": getattr(settings, "TYPESENSE_HEALTHCHECK_INTERVAL_SECONDS", 60),
            }
        )

    def __call__(self) -> Client:
        return self


client: Client = SimpleLazyObject(LazyTypesenseClient)

__all__ = ["client"]
