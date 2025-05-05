from enum import Enum, auto
import cadquery as cq
import projects.garbage_sort_box.measurements as m


class PartType(Enum):
    BOTTOM = auto()
    LONG_SIDE = auto()
    LONG_SIDE_INVERSE = auto()
    SHORT_SIDE = auto()
    SHORT_SIDE_INVERSE = auto()


class Builder:
    _part_type_func_map = {
        PartType.BOTTOM: lambda self: self.get_bottom_panel(),
        PartType.LONG_SIDE: lambda self: self.get_long_side_panel(),
        PartType.LONG_SIDE_INVERSE: lambda self: self.get_long_side_panel(True),
        PartType.SHORT_SIDE: lambda self: self.get_short_side_panel(),
        PartType.SHORT_SIDE_INVERSE: lambda self: self.get_short_side_panel(),
    }

    def get_long_side_panel(self, invert_grooves=False) -> cq.Workplane:
        groove_offset = m.BOX_X / 2 - m.PLY_THICKNESS / 2
        groove_face = ">Y" if invert_grooves else "<Y"
        divider_width = 50

        return (
            cq.Workplane("XZ")
            .box(m.BOX_X, m.PANEL_Z, m.PLY_THICKNESS)
            .faces(groove_face)
            .workplane()
            .pushPoints([(groove_offset, 0), (-groove_offset, 0)])
            .rect(m.PLY_THICKNESS, m.PANEL_Z)
            .cutBlind(-m.ROUTE_DEPTH)
            .faces(groove_face)
            .workplane()
            .moveTo(0, (m.PANEL_Z - divider_width) / 2)
            .rect(m.PLY_THICKNESS, divider_width)
            .cutBlind(-m.ROUTE_DEPTH)
        )

    def get_bottom_panel(self) -> cq.Workplane:
        return (
            cq.Workplane("XY")
            .box(m.BOX_X, m.BOX_Y, m.PLY_THICKNESS - m.ROUTE_DEPTH)
            .faces(">Z")
            .workplane()
            .rect(m.BOX_X - m.PLY_THICKNESS * 2, m.BOX_Y - m.PLY_THICKNESS * 2)
            .extrude(m.ROUTE_DEPTH)
        )

    def get_short_side_panel(self) -> cq.Workplane:
        return cq.Workplane("YZ").box(m.PANEL_Y, m.PANEL_Z, m.PLY_THICKNESS)


    def build_part(self, part_type: PartType) -> cq.Workplane:
        if part_type not in PartType:
            raise ValueError(f"Invalid part type: {part_type}")

        part_func = self._part_type_func_map[part_type]
        return part_func(self)
