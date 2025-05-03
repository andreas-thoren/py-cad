import cadquery as cq
import measurements as m
from parts import PartType, PARTS, PARTS_METADATA


class Assembler:
    """To update/add parts, modify `PartType`, `PARTS` and `PARTS_METADATA` in parts.py."""

    z_offset = m.BOX_Z / 2

    @property
    def x_offset(self):
        return ((m.BOX_X - m.PLY_THICKNESS) / 2) + self.visual_offset

    @property
    def y_offset(self):
        return ((m.BOX_Y - m.PLY_THICKNESS) / 2) + self.visual_offset

    def __init__(self, part_types: list | None = None, visual_offset: int = 0):
        self.part_types = part_types or list(PartType)
        self.visual_offset = visual_offset

    def assemble(self) -> cq.Assembly:
        assy = cq.Assembly()
        for part_type in self.part_types:
            part = PARTS[part_type]
            data = PARTS_METADATA[part_type].copy()
            if callable(data.get("loc")):
                data["loc"] = data["loc"](self)
            assy.add(part, **data)
        return assy
