from enum import Enum
import cadquery as cq
import measurements as m


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


class Part(Enum):
    BOTTOM: cq.Workplane = _Builder.get_bottom_panel()
    LONG_SIDE: cq.Workplane = _Builder.get_long_side_panel()
    LONG_SIDE_INVERSE: cq.Workplane = _Builder.get_long_side_panel(True)
    SHORT_SIDE: cq.Workplane = _Builder.get_short_side_panel()
    SHORT_SIDE_INVERSE: cq.Workplane = _Builder.get_short_side_panel()
