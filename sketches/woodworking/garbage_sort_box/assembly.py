import cadquery as cq
import measurements as m
from parts import Part


class Assembler:
    """To update/add parts, modify the `parts_data` property."""

    z_offset = m.BOX_Z / 2

    @property
    def x_offset(self):
        return ((m.BOX_X - m.PLY_THICKNESS) / 2) + self.visual_offset

    @property
    def y_offset(self):
        return ((m.BOX_Y - m.PLY_THICKNESS) / 2) + self.visual_offset

    def __init__(self, parts: list | None = None, visual_offset: int = 0):
        self.parts = parts or list(Part)
        self.visual_offset = visual_offset

    @property
    def parts_data(self):
        # pylint: disable=no-value-for-parameter
        parts = {
            Part.BOTTOM: {
                "name": "Bottom Panel",
                "color": cq.Color("burlywood"),
            },
            Part.LONG_SIDE: {
                "loc": cq.Location(cq.Vector((0, self.y_offset, self.z_offset))),
                "name": "Long side panel",
                "color": cq.Color("burlywood2"),
            },
            Part.LONG_SIDE_INVERSE: {
                "loc": cq.Location(cq.Vector((0, -self.y_offset, self.z_offset))),
                "name": "Long side panel inverse",
                "color": cq.Color("burlywood2"),
            },
            Part.SHORT_SIDE: {
                "loc": cq.Location(cq.Vector((self.x_offset, 0, self.z_offset))),
                "name": "Short side panel",
                "color": cq.Color("burlywood4"),
            },
            Part.SHORT_SIDE_INVERSE: {
                "loc": cq.Location(cq.Vector((-self.x_offset, 0, self.z_offset))),
                "name": "Short side panel inverse",
                "color": cq.Color("burlywood4"),
            },
        }

        return {key: value for key, value in parts.items() if key in self.parts}

    def assemble(self):
        assembly = cq.Assembly()
        for part, data in self.parts_data.items():
            assembly.add(part.value, **data)
        return assembly
