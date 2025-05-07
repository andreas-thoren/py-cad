from collections.abc import Iterable
import cadquery as cq
from helpers.models import DimensionData
from .assembly import Assembler
from .parts import Builder, PartType


def get_assembled_box(
    box_dimensions: DimensionData,
    assembly_parts: Iterable[PartType] | None = None,
    visual_offset=0,
) -> cq.Assembly:
    assembler = Assembler(box_dimensions, visual_offset)
    return assembler.assemble(assembly_parts=assembly_parts)


def get_box_part(box_dimensions: DimensionData, part_type: PartType) -> cq.Workplane:
    builder = Builder(box_dimensions)
    return builder.build_part(part_type)
