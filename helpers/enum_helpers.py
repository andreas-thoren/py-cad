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

def normalize_key(key: str) -> str:
    return key.strip().upper().replace(" ", "_")

def normalize_value(value: str) -> str:
    return value.strip().lower()

def create_str_enum(
    class_name: str,
    members: Iterable[str],
) -> type[StrEnum]:
    """
    Create a new StrEnum class from an iterable of strings.

    Args:
        class_name: The name of the new enum class.
        members: An iterable of strings (auto-normalized to uppercase keys and lowercase values)

    Returns:
        A dynamically created StrEnum class.

    Raises:
        ValueError: If duplicate keys or values are detected. Duplicate keys are checked when
                    passing an iterable; duplicate values are checked when passing a dict.
    """
    enum_dict = {}

    if isinstance(members, dict):
        value_to_key_map = {}
        for key, val in members.items():
            val = normalize_value(val) if normalize_values else val
            if val in value_to_key_map:
                old_key = value_to_key_map[val]
                del enum_dict[old_key]
            key = normalize_key(key) if normalize_keys else key
            value_to_key_map[val] = key
            enum_dict[key] = val
    else:
        for member in members:
            key = normalize_key(member)
            val = normalize_value(member)
            enum_dict[key] = val

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
    elif isinstance(new_members, dict):
        pass
    else:
        new_members = {
            normalize_key(member): normalize_value(member) for member in new_members
        }

    if not replace_dup_members:
        duplicates = set(enum_dict.keys()) & set(new_members.keys())
        if duplicates:
            _raise_duplicate_val_error(duplicates, is_key=True)

    enum_dict.update(new_members)
    class_name = class_name if class_name else enum_class.__name__
    return create_str_enum(class_name, enum_dict)

def check_enum_normalization(str_enum: type[StrEnum], raise_msg: str = ""):
    unnorm_keys = []
    unnorm_values = []

    for member in str_enum:
        key = member.name
        if key != normalize_key(key):
            unnorm_keys.append(key)
        value = member.value
        if value != normalize_value(value):
            unnorm_values.append(value)
    
    if unnorm_keys or unnorm_values:
        raise ValueError(
            f"The following enum names are not normalized:\n{unnorm_keys}\n"
            f"The following enum values are not normalized:\n{unnorm_values}\n"
            f"{raise_msg}"
        )

