"""
Utilities for dynamically creating and extending StrEnum classes.
This module also supports exporting enums as Python source code for reuse.
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
    
    Note:
        Will silently remove duplicate entries.
    """
    enum_dict = {}
    for member in members:
        key = normalize_key(member)
        val = normalize_value(member)
        enum_dict[key] = val

    enum_cls = StrEnum(class_name, enum_dict)
    return enum_cls


def extend_str_enum(
    enum_class: type[StrEnum],
    new_members: type[StrEnum] | Iterable[str],
    class_name: str = "",
) -> type[StrEnum]:
    """
    Extend a StrEnum class with new members.

    Args:
        enum_class: The base StrEnum to extend.
        new_members: Iterable of str or another StrEnum to add.
        class_name: Optional name for the new extended enum class.

    Returns:
        A new StrEnum class combining old and new members.
    
    Note:
        Members in the first enum will be silently replaced if identically named
        new member exist. The corresponding old value will be replaced with the new.
    """
    enum_dict = {member.name: member.value for member in enum_class}

    if isinstance(new_members, type) and issubclass(new_members, StrEnum):
        new_members = {member.name: member.value for member in new_members}
    else:
        new_members = {
            normalize_key(member): normalize_value(member) for member in new_members
        }

    enum_dict.update(new_members)
    class_name = class_name if class_name else enum_class.__name__
    return create_str_enum(class_name, enum_dict)
