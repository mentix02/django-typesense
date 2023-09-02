import time
from typing import Any

from django_typesense.fields import Field
from django_typesense.fields.number import LongField


class BooleanField(Field):
    def from_value(self, value: Any) -> bool:
        return bool(value)

    def __init__(self, *args, **kwargs):
        kwargs["field_type"] = "bool"
        super().__init__(*args, **kwargs)


class DateField(LongField):
    def from_value(self, value: Any) -> int:
        """
        Expects value to be a datetime.date object.
        """
        return super().from_value(time.mktime(value.timetuple()))


class TimeField(LongField):
    def from_value(self, value: Any) -> int:
        """
        Expects value to be a datetime.time object.
        """
        return super().from_value(time.mktime(value.timetuple()))


class DateTimeField(LongField):
    def from_value(self, value: Any) -> int:
        """
        Expects value to be a datetime.datetime object.
        """
        return super().from_value(time.mktime(value.timetuple()))
