import sketches.garbage_sort_box.measurements as m
from helpers.assembler import assembler_factory
from .parts import parts


Assembler = assembler_factory(
    parts_data=parts,
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
