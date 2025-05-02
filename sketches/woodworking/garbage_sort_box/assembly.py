from measurements import BOX_WIDTH, BOX_LENGTH, BOX_HEIGHT, PLY_THICKNESS, ROUTE_DEPTH
from parts import get_bottom_panel, get_long_side_panel

bottom_panel = get_bottom_panel(BOX_LENGTH, BOX_WIDTH, PLY_THICKNESS, ROUTE_DEPTH)
long_side_panel = get_long_side_panel(BOX_LENGTH, BOX_HEIGHT, PLY_THICKNESS, ROUTE_DEPTH)

# show_object(bottom_panel, name="Bottom Panel")
show_object(long_side_panel, name="Long Side Panel")
