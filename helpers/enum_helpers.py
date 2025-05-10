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


def create_str_enum(
    class_name: str, members: Iterable[str] | dict[str, str]
) -> type[StrEnum]:
    if isinstance(members, dict):
        enum_dict = members.copy()
    else:
        enum_dict = {
            member.upper().replace(" ", "_"): member.lower() for member in members
        }

    enum_cls = StrEnum(class_name, enum_dict)
    enum_cls.write_enum_file = classmethod(write_enum_file)
    return enum_cls


def extend_str_enum(
    enum_class: type[StrEnum],
    new_members: Iterable[str] | dict[str, str],
    name: str = "",
) -> type[StrEnum]:
    enum_dict = {member.name: member.value for member in enum_class}

    if isinstance(new_members, dict):
        enum_dict.update(new_members)
    else:
        enum_dict.update(
            {member.upper().replace(" ", "_"): member.lower() for member in new_members}
        )

    class_name = name if name else enum_class.__name__
    return create_str_enum(class_name, enum_dict)
