from typing import Any

from django_typesense.fields import BaseField


class StringField(BaseField):
    def from_value(self, value: Any) -> str:
        return str(value)

    def __init__(self, *args, **kwargs):
        kwargs["field_type"] = "string"
        super().__init__(*args, **kwargs)


class EmailField(StringField):
    def __init__(self, *args, **kwargs):
        kwargs["token_separators"] = {"+", "-", "@", "."}
        super().__init__(*args, **kwargs)
