from collections.abc import Iterable
import cadquery as cq
from projects.garbage_sort_box.parts import PartType, Builder


class Assembler:
    """To update/add parts, modify the `parts_data` property."""

    PartEnum = PartType

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        width: int | float,
        depth: int | float,
        height: int | float,
        material_thickness: int | float,
        visual_offset: int = 0,
    ):
        self.builder = Builder()
        self._x_length = width
        self._y_length = depth
        self._z_length = height
        self._material_thickness = material_thickness
        self.visual_offset = visual_offset

    @property
    def x_offset(self):
        return ((self._x_length - self._material_thickness) / 2) + self.visual_offset

    @property
    def y_offset(self):
        return ((self._y_length - self._material_thickness) / 2) + self.visual_offset

    @property
    def z_offset(self):
        return self._z_length / 2

    @property
    def metadata_map(self) -> dict[PartEnum, dict]:
        # pylint: disable=no-value-for-parameter
        return {
            PartType.BOTTOM: {
                "loc": cq.Location(cq.Vector(0, 0, 0)),
                "name": "Bottom Panel",
                "color": cq.Color("burlywood"),
            },
            PartType.LONG_SIDE: {
                "loc": cq.Location(cq.Vector(0, self.y_offset, self.z_offset)),
                "name": "Long side panel",
                "color": cq.Color("burlywood2"),
            },
            PartType.LONG_SIDE_INVERSE: {
                "loc": cq.Location(cq.Vector(0, -self.y_offset, self.z_offset)),
                "name": "Long side panel inverse",
                "color": cq.Color("burlywood2"),
            },
            PartType.SHORT_SIDE: {
                "loc": cq.Location(cq.Vector(self.x_offset, 0, self.z_offset)),
                "name": "Short side panel",
                "color": cq.Color("burlywood4"),
            },
            PartType.SHORT_SIDE_INVERSE: {
                "loc": cq.Location(cq.Vector(-self.x_offset, 0, self.z_offset)),
                "name": "Short side panel inverse",
                "color": cq.Color("burlywood4"),
            },
        }

    def get_assembly_data(
        self, assembly_parts: Iterable[PartEnum]
    ) -> list[tuple[cq.Workplane, dict]]:

        assembly_data = []
        metadata_map = self.metadata_map
        for part in assembly_parts:
            try:
                metadata = metadata_map[part]
            except KeyError as exc:
                raise ValueError(f"Invalid part type: {part}") from exc

            cq_workplane = self.builder.build_part(part)
            assembly_data.append((cq_workplane, metadata))
        return assembly_data

    def assemble(self, assembly_parts: Iterable[PartEnum] | None = None) -> cq.Assembly:
        assembly_parts = assembly_parts or tuple(self.PartEnum)
        assembly = cq.Assembly()
        for part, metadata in self.get_assembly_data(assembly_parts):
            assembly.add(part, **metadata)
        return assembly
