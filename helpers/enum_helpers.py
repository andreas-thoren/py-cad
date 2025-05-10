"""
Utilities for dynamically creating and extending StrEnum classes in a safe and controlled way.

This module ensures that dynamically created enums have no duplicate keys or values,
and supports exporting enums as Python source code for reuse. Extending enums is also
supported with optional overwrite behavior.
"""

from collections.abc import Iterable
from enum import StrEnum


def write_enum_file(cls: type[StrEnum], path: str, mode: str = "x"):
    """
    Write a StrEnum class definition to a Python file.

    Args:
        cls: The StrEnum class to export.
        path: File path to write to.
        mode: File mode ('x', 'w', or 'a').
              'x' - exclusive creation (fails if file exists),
              'w' - overwrite,
              'a' - append.

    Raises:
        ValueError: If the mode is not one of 'x', 'w', or 'a'.
    """
    if not mode in {"x", "w", "a"}:
        raise ValueError("Mode should be 'x', 'w' or 'a'")

    lines = ["\n"] if mode == "a" else ["from enum import StrEnum", ""]
    lines.append(f"class {cls.__name__}(StrEnum):")
    for member in cls:
        lines.append(f'    {member.name} = "{member.value}"')

    with open(path, mode, encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _raise_duplicate_val_error(duplicate_set: set[str], is_key: bool = False):
    descriptor = "keys" if is_key else "values"
    duplicates = ", ".join(f"{key}" for key in duplicate_set)
    raise ValueError(
        f"The following {descriptor} have duplicates: '{duplicates}'. "
        "Dynamically created StrEnum:s cannot contain duplicates (neither keys nor values)"
    )


def create_str_enum(
    class_name: str,
    members: Iterable[str] | dict[str, str],
) -> type[StrEnum]:
    """
    Create a new StrEnum class from a list of strings or a dictionary of name-value pairs.

    Args:
        class_name: The name of the new enum class.
        members: An iterable of strings (auto-normalized to uppercase keys and lowercase values)
                 or a dict with explicit key-value mappings.

    Returns:
        A dynamically created StrEnum class.

    Raises:
        ValueError: If duplicate keys or values are detected. Duplicate keys are checked when
                    passing an iterable; duplicate values are checked when passing a dict.
    """
    enum_dict = {}
    duplicates = set()

    if isinstance(members, dict):
        value_set = set()
        for key, val in members.items():
            if val in value_set:
                duplicates.add(val)
            value_set.add(val)
            enum_dict[key] = val
        if duplicates:
            _raise_duplicate_val_error(duplicates)
    else:
        for member in members:
            key = member.upper().replace(" ", "_")
            val = member.lower()
            if key in enum_dict:
                duplicates.add(key)
            enum_dict[key] = val
        if duplicates:
            _raise_duplicate_val_error(duplicates, is_key=True)

    enum_dict = {key.strip(): val.strip() for key, val in enum_dict.items()}
    enum_cls = StrEnum(class_name, enum_dict)
    return enum_cls


def extend_str_enum(
    enum_class: type[StrEnum],
    new_members: type[StrEnum] | dict[str, str] | Iterable[str],
    class_name: str = "",
    replace_dup_members: bool = False,
) -> type[StrEnum]:
    """
    Extend a StrEnum class with new members.

    Args:
        enum_class: The base StrEnum to extend.
        new_members: Iterable of str, dict, or another StrEnum to add.
        class_name: Optional name for the new extended enum class.
        replace_dup_members: If True, allows overwriting existing keys (member.name).
            If False, raises ValueError on conflict.

    Returns:
        A new StrEnum class combining old and new members.
    """
    enum_dict = {member.name: member.value for member in enum_class}

    if isinstance(new_members, type) and issubclass(new_members, StrEnum):
        new_members = {member.name: member.value for member in new_members}
    elif not isinstance(new_members, dict):
        new_members = {
            member.upper().replace(" ", "_"): member.lower() for member in new_members
        }

    if not replace_dup_members:
        duplicates = set(enum_dict.keys()) & set(new_members.keys())
        if duplicates:
            _raise_duplicate_val_error(duplicates, is_key=True)

    enum_dict.update(new_members)
    class_name = class_name if class_name else enum_class.__name__
    return create_str_enum(class_name, enum_dict)
