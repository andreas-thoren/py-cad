from collections.abc import Hashable, Iterable
from typing import Protocol
import cadquery as cq
import measurements as m
from parts import PartType, PARTS, PARTS_METADATA


class AssemblerProtocol(Protocol):
    def assemble(self) -> cq.Assembly:
        pass


def assembler_factory(
    parts_data: Iterable[tuple[Hashable, cq.Workplane, dict]],
    cls_attributes: dict | None = None,
    inst_attributes: dict | None = None,
) -> type[AssemblerProtocol]:

    def __init__(
        self: AssemblerProtocol, part_keys: list | None = None, **kwargs
    ):
        self.part_keys = part_keys or list(self.part_types)
        optional_attributes = inst_attributes.copy() if inst_attributes else {}

        attributes_to_set = {}
        for key, value in kwargs.items():
            if key not in optional_attributes:
                raise AttributeError(
                    f"Invalid attribute '{key}' provided to {self.__class__.__name__}.\n"
                    f"Allowed attributes are: {optional_attributes.keys()}\n"
                )
            attributes_to_set[key] = value
            del optional_attributes[key]

        attributes_to_set.update(optional_attributes)
        for key, value in attributes_to_set.items():
            setattr(self, key, value)


    def assemble(self) -> cq.Assembly:
        assy = cq.Assembly()
        for part_key in self.part_keys:
            part = PARTS[part_key]
            data = PARTS_METADATA[part_key].copy()
            if callable(data.get("loc")):
                data["loc"] = data["loc"](self)
            assy.add(part, **data)
        return assy

    part_types = set()
    parts = {}
    parts_metadata = {}
    for part in parts_data:
        part_name = part[0]
        part_type = part[1]
        part_metadata = part[2]
        part_types.add(part_name)
        parts[part_name] = part_type
        parts_metadata[part_name] = part_metadata

    attributes = cls_attributes or {}
    attributes["__init__"] = __init__
    attributes["assemble"] = assemble
    attributes["part_types"] = part_types
    attributes["parts"] = parts
    attributes["parts_metadata"] = parts_metadata
    return type("Assembler", (AssemblerProtocol,), attributes)


Assembler = assembler_factory(
    tuple(zip(PartType, PARTS.values(), PARTS_METADATA.values())),
    cls_attributes={
        "z_offset": m.BOX_Z / 2,
        "x_offset": property(
            lambda self: ((m.BOX_X - m.PLY_THICKNESS) / 2) + self.visual_offset
        ),
        "y_offset": property(
            lambda self: ((m.BOX_Y - m.PLY_THICKNESS) / 2) + self.visual_offset
        ),
    },
    inst_attributes={"visual_offset": 0},
)
