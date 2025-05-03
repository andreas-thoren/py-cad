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
    """
    Creates a customized Assembler class for assembling cadquery parts.

    Args:
        parts_data: An iterable of (key, cq_object, metadata) tuples.
            - 'key' must be hashable. It identifies potential parts in the assembly.
              Defines valid list items for part_keys upon instantiation.
            - 'cq_object' must be a cadquery Workplane.
            - 'metadata' is a dictionary describing part properties such as color or location.
               metadata keys should match valid keyword arguments for the cq.Assembly.add method.
               metadata values can be static or callables (e.g., lambdas).
               Callables will be evaluated at assembly time, passing the instance as argument.

        cls_attributes: Optional dictionary of class-level attributes to inject,
            typically constants or computed properties.
            Useful for metadata callables that depend on assembler properties (e.g., x_offset, y_offset).

        inst_attributes: Optional dictionary of allowed instance attributes with default values.
            These can be overridden per instance and accessed by metadata callables during assembly.

    Returns:
        A dynamically generated Assembler class.
    """

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
