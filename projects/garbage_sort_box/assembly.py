import cadquery as cq
import projects.garbage_sort_box.measurements as m
from projects.garbage_sort_box.parts import PartType, Builder


class Assembler:
    """To update/add parts, modify the `parts_data` property."""

    z_offset = m.BOX_Z / 2

    @property
    def x_offset(self):
        return ((m.BOX_X - m.PLY_THICKNESS) / 2) + self.visual_offset

    @property
    def y_offset(self):
        return ((m.BOX_Y - m.PLY_THICKNESS) / 2) + self.visual_offset

    def __init__(self, parts: list[PartType] | None = None, visual_offset: int = 0):
        self.parts = parts or list(PartType)
        self.visual_offset = visual_offset
        self.builder = Builder()

    @property
    def assembly_data(self):
        # pylint: disable=no-value-for-parameter
        metadata_map = {
            PartType.BOTTOM: {
                "name": "Bottom Panel",
                "color": cq.Color("burlywood"),
            },
            PartType.LONG_SIDE: {
                "loc": cq.Location(cq.Vector((0, self.y_offset, self.z_offset))),
                "name": "Long side panel",
                "color": cq.Color("burlywood2"),
            },
            PartType.LONG_SIDE_INVERSE: {
                "loc": cq.Location(cq.Vector((0, -self.y_offset, self.z_offset))),
                "name": "Long side panel inverse",
                "color": cq.Color("burlywood2"),
            },
            PartType.SHORT_SIDE: {
                "loc": cq.Location(cq.Vector((self.x_offset, 0, self.z_offset))),
                "name": "Short side panel",
                "color": cq.Color("burlywood4"),
            },
            PartType.SHORT_SIDE_INVERSE: {
                "loc": cq.Location(cq.Vector((-self.x_offset, 0, self.z_offset))),
                "name": "Short side panel inverse",
                "color": cq.Color("burlywood4"),
            },
        }

        assembly_data = []
        for part in self.parts:
            try:
                metadata = metadata_map[part]
            except KeyError as exc:
                raise ValueError(f"Invalid part type: {part}") from exc

            cq_workplane = self.builder.build_part(part)
            assembly_data.append((cq_workplane, metadata))
        return assembly_data

    def assemble(self):
        assembly = cq.Assembly()
        for part, metadata in self.assembly_data:
            assembly.add(part, **metadata)
        return assembly
