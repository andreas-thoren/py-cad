import cadquery as cq
import sketches.garbage_sort_box.measurements as m


# Reusable part utility functions
def _get_long_side_panel(invert_grooves=False):
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


# Create the parts
bottom = (
    cq.Workplane("XY")
    .box(m.BOX_X, m.BOX_Y, m.PLY_THICKNESS - m.ROUTE_DEPTH)
    .faces(">Z")
    .workplane()
    .rect(m.BOX_X - m.PLY_THICKNESS * 2, m.BOX_Y - m.PLY_THICKNESS * 2)
    .extrude(m.ROUTE_DEPTH)
)
short_side = cq.Workplane("YZ").box(m.PANEL_Y, m.PANEL_Z, m.PLY_THICKNESS)
long_side = _get_long_side_panel()
long_side_inverse = _get_long_side_panel(True)
