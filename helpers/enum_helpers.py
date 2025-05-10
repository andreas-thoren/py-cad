from collections.abc import Iterable
from enum import StrEnum


def write_enum_file(cls: type[StrEnum], path: str, mode: str = "x"):
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
    duplicates = (", ".join(f"{key}" for key in duplicate_set))
    raise ValueError(
        f"The following {descriptor} have duplicates: '{duplicates}'. "
        "Dynamically created StrEnum:s cannot contain duplicates (neither keys nor values)"
    )


def create_str_enum(
    class_name: str,
    members: Iterable[str] | dict[str, str],
) -> type[StrEnum]:
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
) -> type[StrEnum]:
    enum_dict = {member.name: member.value for member in enum_class}

    if isinstance(new_members, type) and issubclass(new_members, StrEnum):
        new_members = {member.name: member.value for member in new_members}
    elif not isinstance(new_members, dict):
        new_members = {
            member.upper().replace(" ", "_"): member.lower() for member in new_members
        }

    duplicates = set(enum_dict.keys()) & set(new_members.keys())
    if duplicates:
        _raise_duplicate_val_error(duplicates, is_key=True)

    enum_dict.update(new_members)
    class_name = class_name if class_name else enum_class.__name__
    return create_str_enum(class_name, enum_dict)
