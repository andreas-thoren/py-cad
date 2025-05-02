from measurements import (
    PLY_THICKNESS,
    ROUTE_DEPTH,
    BOX_X,
    BOX_Y,
    BOX_Z,
    DIVIDER_X,
    DIVIDER_Y,
    DIVIDER_Z,
)
from parts import get_bottom_panel, get_long_side_panel

bottom_panel = get_bottom_panel(BOX_X, BOX_Y, PLY_THICKNESS, ROUTE_DEPTH)
long_side_panel = get_long_side_panel(BOX_X, BOX_Z, PLY_THICKNESS, ROUTE_DEPTH)

# pylint: disable=undefined-variable
show_object(long_side_panel, name="Long Side Panel") # type: ignore
