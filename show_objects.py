def show_garbage_sort_box():
    from projects.garbage_sort_box.measurements import DIMENSION_DATA
    from projects.garbage_sort_box.assembly import Assembler, PartType

    assembler = Assembler(DIMENSION_DATA)
    assembly_parts = [PartType.BOTTOM, PartType.LONG_SIDE, PartType.SHORT_SIDE]
    # assembly = assembler.assemble(assembly_parts)
    assembly = assembler.assemble()
    show_object(assembly, name="Garbage Sort Box Assembly")  # type: ignore


def show_generic_box():
    from primitives.basic_box.factory import get_assembled_box, PartType
    from projects.generic_box import BOX_DIMENSIONS

    # part_types = [PartType.BOTTOM, PartType.LONG_SIDE]
    part_types = list(PartType)
    assembly = get_assembled_box(BOX_DIMENSIONS, part_types)
    show_object(assembly, name="Generic box")  # type: ignore

def show_generic_box_part():
    from primitives.basic_box.factory import get_box_part, PartType
    from projects.generic_box import BOX_DIMENSIONS

    part_type = PartType.BOTTOM
    part = get_box_part(BOX_DIMENSIONS, part_type)
    show_object(part, name=part_type.name.replace("_", " ").capitalize())




# show_garbage_sort_box()
# show_generic_box_part()
show_generic_box()
