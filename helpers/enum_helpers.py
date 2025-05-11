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


def normalize_dict(dct: dict[str, str]) -> dict:
    return {normalize_key(key): normalize_value(val) for key, val in dct.items()}


def create_str_enum(
    class_name: str,
    members: Iterable[str] | dict[str, str],
    normalize_members: bool = True,
) -> type[StrEnum]:
    """
    Create a new StrEnum class from an iterable of strings.

    Args:
        class_name: The name of the new enum class.
        members: An iterable of strings. Can also be a dict with explicitly set key/value
            pairs that maps to member.name (key) and member.value (value)
        normalize_members: If True:
            - keys are uppercased, stripped and ' ' replaced with '_'
            - values are lowercased and stripped.

    Returns:
        A dynamically created StrEnum class.

    Note:
        If multiple keys normalize to the same result, the last one wins silently.
    """
    dct = (
        members if isinstance(members, dict) else {member: member for member in members}
    )

    if normalize_members:
        dct = normalize_dict(dct)

    enum_cls = StrEnum(class_name, dct)
    return enum_cls


def extend_str_enum(
    enum_class: type[StrEnum],
    new_members: type[StrEnum] | dict[str, str] | Iterable[str],
    class_name: str = "",
    normalize_new_members: bool = True,
) -> type[StrEnum]:
    """
    Extend a StrEnum class with new members.

    Args:
        enum_class: The base StrEnum to extend.
        new_members: Iterable of str, dict[str, str], or StrEnum to add.
        class_name: Optional name for the new extended enum class.
        normalize_new_members: If True normalises new members:
            - keys are uppercased, stripped and ' ' replaced with '_'
            - values are lowercased and stripped.

    Returns:
        A new StrEnum class combining old and new members.

    Note:
        If a key from `new_members` matches an existing one, it will override the original.
    """
    members = {member.name: member.value for member in enum_class}

    if isinstance(new_members, type) and issubclass(new_members, StrEnum):
        new_members = {member.name: member.value for member in new_members}
    elif not isinstance(new_members, dict):
        new_members = {member: member for member in new_members}

    if normalize_new_members:
        new_members = normalize_dict(new_members)

    members.update(new_members)
    class_name = class_name if class_name else enum_class.__name__

    # Old members should not be normalized and new are handled above
    return create_str_enum(class_name, members, normalize_members=False)
