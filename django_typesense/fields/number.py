from typing import Any

from django_typesense.fields import BaseField
from django_typesense.fields.string import StringField


class IntegerField(BaseField):
    """
    Field to represent 32-bit integers upto 2,147,483,647.
    """

    def from_value(self, value: Any) -> int:
        return int(value)

    def __init__(self, *args, **kwargs):
        kwargs["field_type"] = "int32"
        super().__init__(*args, **kwargs)


class LongField(BaseField):
    """
    Field to represent 64-bit integers larger than 2,147,483,647.
    """

    def from_value(self, value: Any) -> int:
        return int(value)

    def __init__(self, *args, **kwargs):
        kwargs["field_type"] = "int64"
        super().__init__(*args, **kwargs)


class FloatField(BaseField):
    def from_value(self, value: Any) -> Any:
        return float(value)

    def __init__(self, *args, **kwargs):
        kwargs["field_type"] = "float"
        super().__init__(*args, **kwargs)


class PhoneNumberField(StringField):
    """
    PhoneNumberField is a string field that is tokenized by parentheses
    and hyphens. But this probably doesn't strictly belong in the number
    module even though it's a subclass of StringField.
    """

    def __init__(self, *args, **kwargs):
        kwargs["token_separators"] = {"(", ")", "-"}
        super().__init__(*args, **kwargs)
