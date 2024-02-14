from __future__ import annotations

import abc
from typing import Set, Any, Dict, Union, Tuple, Optional


TypesenseFieldKey = str
TypesenseFieldValue = Union[str, bool]
TypesenseFieldType = Dict[TypesenseFieldKey, TypesenseFieldValue]

SingularTypesenseFieldsType = Tuple[TypesenseFieldType]
MultipleTypesenseFieldsType = Tuple[TypesenseFieldType, TypesenseFieldType]


class BaseField(abc.ABC):
    def __init__(
        self,
        field_type: str,
        index: bool = True,
        facet: bool = False,
        optional: bool = False,
        name: Optional[str] = None,  # if set to None, set it to the variable name
        source: Optional[str] = None,
        index_empty_values: bool = False,
        facet_index_empty_values: bool = False,
        token_separators: Optional[Set[str]] = None,  # helpful for tokenizing special strings like URLS, emails, etc.
    ):
        self.index: bool = index
        self.facet: bool = facet
        self.optional: bool = optional
        self.name: Optional[str] = name
        self.field_type: str = field_type
        self.source: Optional[str] = source
        self.index_empty_values: bool = index_empty_values
        self.facet_index_empty_values: bool = facet_index_empty_values

        if token_separators:
            self.token_separators = token_separators or set()

        if self.index_empty_values or self.facet_index_empty_values:
            assert self.optional, (
                "You can only index empty values for an optional field. " "Please set `optional=True`."
            )
            # check if facet_index_empty_values wasn't set without setting index_empty_values
            if self.facet_index_empty_values and not self.index_empty_values:
                msg = (
                    "You can only set facet to boolean indexed empty value fields if you are indexing empty values."
                    "Please set `index_empty_values=True` or `facet_index_empty_values=False`."
                )
                raise AssertionError(msg)

    @property
    def empty_value_boolean_field_name(self) -> str:
        assert self.name is not None, "Please explicitly set `name` for {self.__class__.__name__} field."
        return f"is_{self.name}_null"

    @abc.abstractmethod
    def from_value(self, value: Any) -> Any:
        pass

    def _empty_value_boolean_field(self) -> BaseField:
        # Avoid caching this BooleanField - it may seem tempting
        # since it looks like this field will have to be imported
        # everytime this method is called. But Python caches imports
        # according to it's content and not files. So it takes care
        # of caching it for us! Even if we have to call this field
        # multiple times for a large document with tons of indexable
        # empty fields, it will still be performant after the
        # first ever import. Pretty cool, huh?
        from django_typesense.fields.misc import BooleanField

        return BooleanField(name=f"is_{self.name}_null", facet=self.facet_index_empty_values)

    def to_typesense_field_objs(
        self, name: Optional[str] = None
    ) -> Union[SingularTypesenseFieldsType, MultipleTypesenseFieldsType]:
        """
        Return a tuple of two fields to destructure the individual
        field types into the final schema object's `fields` list.

        With something like -

        >>> import itertools
        >>> from django_typesense.collection import Collection as SomeCollection
        >>> collection = SomeCollection(...)
        >>> fields = list(
        ...     filter(
        ...         lambda attr: isinstance(attr, BaseField),
        ...         (getattr(self, attr_name) for attr_name in dir(self)), # noqa
        ...     ),
        ... )

        Why not just return a dict?

        Because sometimes we may need to add multiple fields for a single
        field type. For example, an `optional` marked field may need to be
        indexed for empty values as well. In that case, we need to create
        the optional field and a boolean `is_<field_name>_null` field.

        Reference - https://tinyurl.com/empty-val-searching
        """

        # Make sure either self.name or name_from_collection_instance is set
        assert (
            self.name is not None or name is not None
        ), f"Please set the `name` field for {self.__class__.__name__} field."

        self.name = self.name or name

        base_field: TypesenseFieldType = {
            "facet": self.facet,
            "index": self.index,
            "name": str(self.name),
            "type": self.field_type,
            "optional": self.optional,
        }

        if self.index_empty_values:
            empty_is_bool_field: TypesenseFieldType = self._empty_value_boolean_field().to_typesense_field_objs()[0]
            return base_field, empty_is_bool_field
        else:
            return (base_field,)
