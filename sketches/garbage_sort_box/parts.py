from enum import Enum, auto
import cadquery as cq
import sketches.garbage_sort_box.measurements as m


class _Builder:
    @staticmethod
    def get_bottom_panel():
        return (
            cq.Workplane("XY")
            .box(m.BOX_X, m.BOX_Y, m.PLY_THICKNESS - m.ROUTE_DEPTH)
            .faces(">Z")
            .workplane()
            .rect(m.BOX_X - m.PLY_THICKNESS * 2, m.BOX_Y - m.PLY_THICKNESS * 2)
            .extrude(m.ROUTE_DEPTH)
        )

    @staticmethod
    def get_short_side_panel():
        return cq.Workplane("YZ").box(m.PANEL_Y, m.PANEL_Z, m.PLY_THICKNESS)

    @staticmethod
    def get_long_side_panel(invert_grooves=False):
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


class PartType(Enum):
    BOTTOM = auto()
    LONG_SIDE = auto()
    LONG_SIDE_INVERSE = auto()
    SHORT_SIDE = auto()
    SHORT_SIDE_INVERSE = auto()


# Mapping of part types to their corresponding cadquery objects
PARTS: dict[PartType, cq.Workplane] = {
    PartType.BOTTOM: _Builder.get_bottom_panel(),
    PartType.LONG_SIDE: _Builder.get_long_side_panel(),
    PartType.LONG_SIDE_INVERSE: _Builder.get_long_side_panel(True),
    PartType.SHORT_SIDE: _Builder.get_short_side_panel(),
    PartType.SHORT_SIDE_INVERSE: _Builder.get_short_side_panel(),
}

# pylint: disable=no-value-for-parameter
# Data for use in the assembly
PARTS_METADATA: dict[PartType, dict] = {
    PartType.BOTTOM: {
        "name": "Bottom Panel",
        "color": cq.Color("burlywood"),
    },
    PartType.LONG_SIDE: {
        "name": "Long side panel",
        "color": cq.Color("burlywood2"),
        "loc": lambda assembler: cq.Location(
            cq.Vector((0, assembler.y_offset, assembler.z_offset))
        ),
    },
    PartType.LONG_SIDE_INVERSE: {
        "name": "Long side panel inverse",
        "color": cq.Color("burlywood2"),
        "loc": lambda assembler: cq.Location(
            cq.Vector((0, -assembler.y_offset, assembler.z_offset))
        ),
    },
    PartType.SHORT_SIDE: {
        "name": "Short side panel",
        "color": cq.Color("burlywood4"),
        "loc": lambda assembler: cq.Location(
            cq.Vector((assembler.x_offset, 0, assembler.z_offset))
        ),
    },
    PartType.SHORT_SIDE_INVERSE: {
        "name": "Short side panel inverse",
        "color": cq.Color("burlywood4"),
        "loc": lambda assembler: cq.Location(
            cq.Vector((-assembler.x_offset, 0, assembler.z_offset))
        ),
    },
}
