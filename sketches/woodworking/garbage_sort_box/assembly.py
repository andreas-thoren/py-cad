import cadquery as cq
import measurements as m
from parts import Part


def get_assembly(visual_offset=0):
    x_offset = ((m.BOX_X - m.PLY_THICKNESS) / 2) + visual_offset
    y_offset = ((m.BOX_Y - m.PLY_THICKNESS) / 2) + visual_offset
    z_offset = m.BOX_Z / 2

    # pylint: disable=no-value-for-parameter
    assy = cq.Assembly()
    assy.add(Part.bottom, name="Bottom Panel", color=cq.Color("burlywood"))
    assy.add(
        Part.long_side,
        name="Side Panel",
        loc=cq.Location(cq.Vector(0, y_offset, z_offset)),
        color=cq.Color("burlywood2"),
    )
    assy.add(
        Part.long_side_inverse,
        name="Side Panel inverse",
        loc=cq.Location(cq.Vector(0, -y_offset, z_offset)),
        color=cq.Color("burlywood2"),
    )
    assy.add(
        Part.short_side,
        name="Short Side Panel",
        loc=cq.Location(cq.Vector(x_offset, 0, z_offset)),
        color=cq.Color("burlywood4"),
    )
    assy.add(
        Part.short_side,
        name="Short Side Panel inverse",
        loc=cq.Location(cq.Vector(-x_offset, 0, z_offset)),
        color=cq.Color("burlywood4"),
    )
    return assy


assembly = get_assembly()
