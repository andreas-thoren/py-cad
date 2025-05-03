from collections.abc import Hashable
from enum import Enum, auto
import cadquery as cq
import sketches.garbage_sort_box.measurements as m
from sketches.garbage_sort_box import parts
from helpers.assembler import assembler_factory


# Optional enum to easily reference part types in show_objects.py
class PartType(Enum):
    BOTTOM = auto()
    LONG_SIDE = auto()
    LONG_SIDE_INVERSE = auto()
    SHORT_SIDE = auto()
    SHORT_SIDE_INVERSE = auto()


# pylint: disable=no-value-for-parameter
# Define parts_data according to the assembler_factory function signature
parts_data: tuple[tuple[Hashable, cq.Workplane, dict]] = (
    (
        PartType.BOTTOM,
        parts.bottom,
        {
            "name": "Bottom Panel",
            "color": cq.Color("burlywood"),
        },
    ),
    (
        PartType.LONG_SIDE,
        parts.long_side,
        {
            "name": "Long side panel",
            "color": cq.Color("burlywood2"),
            "loc": lambda assembler: cq.Location(
                cq.Vector((0, assembler.y_offset, assembler.z_offset))
            ),
        },
    ),
    (
        PartType.LONG_SIDE_INVERSE,
        parts.long_side_inverse,
        {
            "name": "Long side panel inverse",
            "color": cq.Color("burlywood2"),
            "loc": lambda assembler: cq.Location(
                cq.Vector((0, -assembler.y_offset, assembler.z_offset))
            ),
        },
    ),
    (
        PartType.SHORT_SIDE,
        parts.short_side,
        {
            "name": "Short side panel",
            "color": cq.Color("burlywood4"),
            "loc": lambda assembler: cq.Location(
                cq.Vector((assembler.x_offset, 0, assembler.z_offset))
            ),
        },
    ),
    (
        PartType.SHORT_SIDE_INVERSE,
        parts.short_side,
        {
            "name": "Short side panel inverse",
            "color": cq.Color("burlywood4"),
            "loc": lambda assembler: cq.Location(
                cq.Vector((-assembler.x_offset, 0, assembler.z_offset))
            ),
        },
    ),
)

# Create the Assembler class using the assembler_factory function
Assembler = assembler_factory(
    parts_data=parts_data,
    cls_attributes={
        "z_offset": m.BOX_Z / 2,
        "x_offset": property(
            lambda self: ((m.BOX_X - m.PLY_THICKNESS) / 2) + self.visual_offset
        ),
        "y_offset": property(
            lambda self: ((m.BOX_Y - m.PLY_THICKNESS) / 2) + self.visual_offset
        ),
    },
    inst_attributes={"visual_offset": 0},
)
