import cadquery as cq
from measurements import (
    PLY_THICKNESS,
    BOX_X,
    BOX_Y,
    BOX_Z,
)
from parts import get_bottom_panel, get_long_side_panel, get_short_side_panel

bottom_panel = get_bottom_panel()
long_side_panel = get_long_side_panel()
long_side_panel_inverse = get_long_side_panel(True)
short_side_panel = get_short_side_panel()

def get_assembly(visual_offset=0):
    x_offset = ((BOX_X - PLY_THICKNESS) / 2) + visual_offset
    y_offset = ((BOX_Y - PLY_THICKNESS) / 2) + visual_offset
    z_offset = BOX_Z / 2

    # pylint: disable=no-value-for-parameter
    assy = cq.Assembly()
    assy.add(bottom_panel, name="Bottom Panel", color=cq.Color("burlywood"))
    assy.add(
        long_side_panel,
        name="Side Panel",
        loc=cq.Location(cq.Vector(0, y_offset, z_offset)),
        color=cq.Color("burlywood2"),
    )
    assy.add(
        long_side_panel_inverse,
        name="Side Panel inverse",
        loc=cq.Location(cq.Vector(0, -y_offset, z_offset)),
        color=cq.Color("burlywood2"),
    )
    assy.add(
        short_side_panel,
        name="Short Side Panel",
        loc=cq.Location(cq.Vector(x_offset, 0, z_offset)),
        color=cq.Color("burlywood4"),
    )
    assy.add(
        short_side_panel,
        name="Short Side Panel inverse",
        loc=cq.Location(cq.Vector(-x_offset, 0, z_offset)),
        color=cq.Color("burlywood4"),
    )
    return assy

assembly = get_assembly()

try:
    show_object(assembly)  # type: ignore
except NameError:
    if __name__ == "__main__":
        print("Exporting assembly to .step for use in freecad.")
        assembly.export("garbage_sort_box_assembly.step")
