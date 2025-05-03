from collections.abc import Hashable, Iterable
import cadquery as cq


def assembler_factory(
    parts_data: Iterable[tuple[Hashable, cq.Workplane, dict]],
    cls_attributes: dict | None = None,
    inst_attributes: dict | None = None,
) -> type:

    class Assembler:
        part_types = set()
        parts = {}
        parts_metadata = {}

        def __init__(self, part_keys: list | None = None, **kwargs):
            self.part_keys = part_keys or list(Assembler.part_types)
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
                part = self.parts[part_key]
                metadata = self.parts_metadata[part_key].copy()

                for key, value in metadata.items():
                    if callable(value):
                        metadata[key] = value(self)

                assy.add(part, **metadata)
            return assy

    for part in parts_data:
        part_name, part_type, part_metadata = part
        Assembler.part_types.add(part_name)
        Assembler.parts[part_name] = part_type
        Assembler.parts_metadata[part_name] = part_metadata

    if cls_attributes:
        for key, value in cls_attributes.items():
            setattr(Assembler, key, value)

    return Assembler
