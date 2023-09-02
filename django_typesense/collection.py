import abc
from functools import cache
from typing import Any, List, Type, Dict, Optional

from django.db.models import Model

from django_typesense.fields import BaseField, TypesenseFieldType
from django_typesense.fields.number import LongField, FloatField, IntegerField


NameFieldDict = Dict[str, TypesenseFieldType]


class Collection(abc.ABC):
    @cache
    def _get_typesense_fields(self) -> List[TypesenseFieldType]:
        """
        Returns a list of Typesense field objects for the Collection.
        Also applies the attr_name to the field is a name wasn't set.
        """
        fields: List[TypesenseFieldType] = []

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, BaseField):
                attr_fields = attr.to_typesense_field_objs(attr_name)
                fields.extend(attr_fields)

        return fields

    @cache
    def _get_fields_dict(self) -> Dict[str, BaseField]:
        """
        Returns a dict of Field objects with their attr_name
        (or provided name) as the key.
        """
        fields = {}

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, BaseField):
                fields[attr.name or attr_name] = attr

        return fields

    def to_typesense_schema(self) -> Dict[str, Any]:
        collection_name = self.Meta.name
        class_name = self.__class__.__name__

        assert hasattr(self, "Meta"), f"Please set a Meta class for {class_name} Collection."

        assert collection_name is not None and isinstance(
            collection_name, str
        ), f"Please set Meta.name to a str for {class_name} Collection."

        model_class: Optional[Type[Model]] = self.Meta.model

        assert (
            model_class is not None and issubclass(model_class, Model) and not model_class._meta.abstract
        ), f"Model for Collection {class_name} can't be {type(model_class)} or an abstract model."

        typesense_fields = self._get_typesense_fields()

        assert len(typesense_fields) > 0, f"Collection {class_name} has no fields. Please add at least one field."

        schema = {
            "name": collection_name,
            "fields": typesense_fields,
        }

        if hasattr(self.Meta, "order_by") and self.Meta.order_by is not None:
            # check if the `order_by` field is a valid IntegerField or FloatField

            for name, field in self._get_fields_dict().items():
                if name == self.Meta.order_by:
                    if not issubclass(type(field), (LongField, FloatField, IntegerField)):
                        raise ValueError(
                            f"order_by field '{self.Meta.order_by}' is not an "
                            f"IntegerField or FloatField in collection '{class_name}'."
                            f"Got {type(field)} instead."
                        )
                    elif field.optional:
                        raise ValueError(
                            f"order_by field '{self.Meta.order_by}' cannot be optional "
                            f"in collection '{class_name}'."
                        )
                    break
            else:
                raise ValueError(f"Field {self.Meta.order_by} does not exist in collection '{class_name}'.")

            schema["default_sorting_field"] = self.Meta.order_by

        return schema

    class Meta:
        """
        The `name` & `model` fields aren't "Optional". They're
        only decorated so to please mypy. They're compulsory
        Make sure to set them in your subclass.
        """

        name: Optional[str] = None
        model: Optional[Type[Model]] = None

        # name of an numerical field to use for sorting results.
        # Typesense only supports sorting by a single field.
        order_by: Optional[str] = None
