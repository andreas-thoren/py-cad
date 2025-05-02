import cadquery as cq
from measurements import (
    PLY_THICKNESS,
    BOX_X,
    BOX_Y,
    BOX_Z,
)
from parts import get_bottom_panel, get_long_side_panel, get_short_side_panel

# create the parts
bottom_panel = get_bottom_panel()
long_side_panel = get_long_side_panel()
long_side_panel_inverse = get_long_side_panel(True)
short_side_panel = get_short_side_panel()

# assemble the parts
# pylint: disable=no-value-for-parameter
assy = cq.Assembly()
assy.add(bottom_panel, name="Bottom Panel", color=cq.Color("burlywood"))
assy.add(
    long_side_panel,
    name="Side Panel",
    loc=cq.Location(cq.Vector(0, (BOX_Y - PLY_THICKNESS) / 2, BOX_Z / 2)),
    color=cq.Color("burlywood2"),
)
assy.add(
    long_side_panel_inverse,
    name="Side Panel inverse",
    loc=cq.Location(cq.Vector(0, -(BOX_Y - PLY_THICKNESS) / 2, BOX_Z / 2)),
    color=cq.Color("burlywood2"),
)
assy.add(
    short_side_panel,
    name="Short Side Panel",
    loc=cq.Location(cq.Vector((BOX_X - PLY_THICKNESS) / 2, 0, BOX_Z / 2)),
    color=cq.Color("burlywood4"),
)
assy.add(
    short_side_panel,
    name="Short Side Panel inverse",
    loc=cq.Location(cq.Vector(-(BOX_X - PLY_THICKNESS) / 2, 0, BOX_Z / 2)),
    color=cq.Color("burlywood4"),
)

# pylint: disable=undefined-variable
show_object(assy)  # type: ignore
