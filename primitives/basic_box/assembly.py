from collections.abc import Hashable
import cadquery as cq
from helpers.assembler import assembler_factory
from primitives.basic_box.parts import get_long_side_panel, get_short_side_panel, get_bottom_panel, PartType

# pylint: disable=no-value-for-parameter
# Define parts_data according to the assembler_factory function signature
def get_parts_data(x_len, y_len, z_len, thickness) -> tuple[tuple[Hashable, cq.Workplane, dict]]:
    route_depth = thickness / 2

    return (
        (
            PartType.BOTTOM,
            get_bottom_panel(x_len, y_len, z_len, thickness, 0),
            {
                "name": "Bottom panel",
                "color": cq.Color("burlywood"),
            },
        ),
        (
            PartType.LONG_SIDE,
            parts.long_side,
            {
                "name": "Long side panel",
                "color": cq.Color("burlywood2"),
                "loc": lambda ass: cq.Location((0, ass.y_offset, ass.z_offset)),
            },
        ),
        (
            PartType.LONG_SIDE_INVERSE,
            parts.long_side_inverse,
            {
                "name": "Long side panel inverse",
                "color": cq.Color("burlywood2"),
                "loc": lambda ass: cq.Location((0, -ass.y_offset, ass.z_offset)),
            },
        ),
        (
            PartType.SHORT_SIDE,
            parts.short_side,
            {
                "name": "Short side panel",
                "color": cq.Color("burlywood4"),
                "loc": lambda ass: cq.Location((ass.x_offset, 0, ass.z_offset)),
            },
        ),
        (
            PartType.SHORT_SIDE_INVERSE,
            parts.short_side,
            {
                "name": "Short side panel inverse",
                "color": cq.Color("burlywood4"),
                "loc": lambda ass: cq.Location((-ass.x_offset, 0, ass.z_offset)),
            },
        ),
    )

def get_assembler(x_len, y_len, z_len, thickness):
    # Create the Assembler class using the assembler_factory function
    return assembler_factory(
        parts_data=get_parts_data(x_len, y_len, z_len, thickness),
        cls_attributes={
            "z_offset": z_len / 2,
            "x_offset": property(
                lambda self: ((x_len - thickness) / 2) + self.visual_offset
            ),
            "y_offset": property(
                lambda self: ((y_len - thickness) / 2) + self.visual_offset
            ),
        },
        inst_attributes={"visual_offset": 0},
    )
