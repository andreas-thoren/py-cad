import cadquery as cq
from measurements import (
    PLY_THICKNESS,
    ROUTE_DEPTH,
    BOX_X,
    BOX_Y,
    PANEL_Y,
    PANEL_Z,
    DIVIDER_X,
    DIVIDER_Y,
    DIVIDER_Z,
)

def get_bottom_panel():
    return (
     cq.Workplane("XY")
     .box(BOX_X, BOX_Y, PLY_THICKNESS-ROUTE_DEPTH)
     .faces(">Z")
     .workplane()
     .rect(BOX_X-PLY_THICKNESS*2, BOX_Y-PLY_THICKNESS*2)
     .extrude(ROUTE_DEPTH)
    )

def get_short_side_panel():
    return (
     cq.Workplane("YZ")
     .box(PANEL_Y, PANEL_Z, PLY_THICKNESS)
    )

def get_long_side_panel(invert_grooves=False):
    groove_offset = BOX_X/2 - PLY_THICKNESS/2
    groove_face = ">Y" if invert_grooves else "<Y"
    divider_width = 50

    return (
        cq.Workplane("XZ")
        .box(BOX_X, PANEL_Z, PLY_THICKNESS)
        .faces(groove_face)
        .workplane()
        .pushPoints([(groove_offset, 0), (-groove_offset, 0)])
        .rect(PLY_THICKNESS, PANEL_Z)
        .cutBlind(-ROUTE_DEPTH)
        .faces(groove_face)
        .workplane()
        .moveTo(0, (PANEL_Z-divider_width)/2)
        .rect(PLY_THICKNESS, divider_width)
        .cutBlind(-ROUTE_DEPTH)
    )
