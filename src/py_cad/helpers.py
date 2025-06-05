from collections import UserDict
from enum import StrEnum
from typing import Any, Generic, TypeVar


class StrAutoEnum(StrEnum):
    """
    StrEnum that automatically assigns values based on the enum member name
    if using auto() (from enum import auto). Values will then be lowercased strings
    of the member names.
    """

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()


K = TypeVar("K")
V = TypeVar("V")


class NormalizedDict(UserDict, Generic[K, V]):
    """
    Used for all dicts where part types are used as keys.
    Normalizes keys to lowercase stripped strings (both for setting/getting items).
    """

    @staticmethod
    def normalize_item(key: K, raise_error: bool = False) -> str | Any:
        """
        Normalize keys to lowercase strings. If raise_error is False will return
        the original key without raising if original key is not a string.
        """
        try:
            return key.strip().lower()
        except AttributeError as exc:
            if raise_error:
                raise TypeError(
                    f"Keys must be strings, got {type(key).__name__}: {key!r}"
                ) from exc
            return key

    def __getitem__(self, key: K) -> V:
        return super().__getitem__(self.normalize_item(key))

    def __setitem__(self, key: K, value: V) -> None:
        super().__setitem__(self.normalize_item(key, raise_error=True), value)

    def __delitem__(self, key: K) -> None:
        super().__delitem__(self.normalize_item(key))

    def __contains__(self, key: K) -> bool:
        return super().__contains__(self.normalize_item(key))


class InheritanceMixin:
    """Provides get_parent_items method to collect and merge inherited attributes."""

    @classmethod
    def get_parent_items(
        cls,
        attr_name: str,
    ) -> set[str] | dict[str, str] | None:
        """
        Return the union of the inherited attribute across the class MRO.
        If collisions are found, the younger (more derived) class's items take precedence.
        If the attribute is not found in any ancestor, returns None.
        """
        # Loop through ancestors creating parent_items
        parent_items = None
        for base in cls.__mro__[1:]:
            older_parent_items = getattr(base, attr_name, None)
            if older_parent_items is None:
                continue

            if parent_items is None:
                parent_items = older_parent_items
            else:
                # Younger parents come first in mro and should override older parents
                parent_items = older_parent_items | parent_items

        return parent_items


class _PostInitMeta(type):
    """
    Metaclass that ensures a '_post_init' method is always called after object construction.
    Intended for use within the core framework only. Do not override `_post_init` in regular
    subclasses. Only customize `_post_init` if extending the framework's base logic.
    """

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        if not hasattr(instance, "_post_init"):
            raise TypeError(
                f"Since class '{cls.__name__}' has metaclass=_PostInitMeta "
                "it must implement a '_post_init' method."
            )
        instance._post_init(*args, **kwargs)
        return instance
