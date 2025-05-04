from enum import Enum, auto
import cadquery as cq


# Optional enum to easily reference part types in show_objects.py
class PartType(Enum):
    BOTTOM = auto()
    LONG_SIDE = auto()
    LONG_SIDE_INVERSE = auto()
    SHORT_SIDE = auto()
    SHORT_SIDE_INVERSE = auto()

# Functions for createing the parts
def get_long_side_panel(x_len, y_len, z_len, route_depth, invert_grooves=False):
    groove_offset = x_len / 2 - y_len / 2
    groove_face = ">Y" if invert_grooves else "<Y"

    return (
        cq.Workplane("XZ")
        .box(x_len, z_len, y_len)
        .faces(groove_face)
        .workplane()
        .pushPoints([(groove_offset, 0), (-groove_offset, 0)])
        .rect(y_len, z_len)
        .cutBlind(-route_depth)
    )

def get_bottom_panel(x_len, y_len, z_len, panel_thickness, route_depth):
    return (
        cq.Workplane("XY")
        .box(x_len, y_len, z_len)
        .faces(">Z")
        .workplane()
        .rect(x_len - panel_thickness * 2, y_len - panel_thickness * 2)
        .cutBlind(-route_depth)
    )

def get_short_side_panel(x_len, y_len, z_len):
    return (
        cq.Workplane("YZ")
        .box(y_len, z_len, x_len)
    )
