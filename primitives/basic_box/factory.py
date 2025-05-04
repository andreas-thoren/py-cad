from collections.abc import Hashable
import cadquery as cq
from .assembly import get_assembler


def get_assembled_box(width, depth, height, thickness, visual_offset=0) -> cq.Assembly:
    AssemblerClass = get_assembler(
        x_len=width, y_len=depth, z_len=height, thickness=thickness
    )
    assembler = AssemblerClass(visual_offset=visual_offset)
    return assembler.assemble()


def get_box_parts(width, depth, height, thickness) -> dict[Hashable, cq.Workplane]:
    pass
