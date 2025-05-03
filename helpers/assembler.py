from collections.abc import Hashable, Iterable
from dataclasses import dataclass
import cadquery as cq


@dataclass
class Part:
    cq_object: cq.Workplane
    metadata: dict


def assembler_factory(
    parts_data: Iterable[tuple[Hashable, cq.Workplane, dict]],
    cls_attributes: dict | None = None,
    inst_attributes: dict | None = None,
) -> type:

    class Assembler:
        parts: dict[Hashable, Part] = {}

        def __init__(self, part_keys: list | None = None, **kwargs):
            self.part_keys = part_keys or list(Assembler.parts.keys())
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
                try:
                    part = self.parts[part_key]
                except KeyError as exc:
                    raise ValueError(
                        f"Part '{part_key}' not found in instance of {self.__class__.__name__}.\n"
                        f"Available parts are: {list(self.parts.keys())}\n"
                    ) from exc

                metadata = part.metadata.copy()
                for key, value in metadata.items():
                    if callable(value):
                        metadata[key] = value(self)

                assy.add(part.cq_object, **metadata)
            return assy
        
        def __repr__(self) -> str:
            attrs = [f"part_keys={self.part_keys}"]
            for key in vars(self):
                if key != "part_keys":
                    attrs.append(f"{key}={getattr(self, key)!r}")
            return f"{self.__class__.__name__}({', '.join(attrs)})"

    for part in parts_data:
        part_key, cq_object, metadata = part
        Assembler.parts[part_key] = Part(cq_object, metadata)

    if cls_attributes:
        for key, value in cls_attributes.items():
            setattr(Assembler, key, value)

    return Assembler
