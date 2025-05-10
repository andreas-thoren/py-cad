def show_garbage_sort_box():
    from projects.garbage_sort_box.project_data import DIMENSION_DATA
    from projects.garbage_sort_box.assembly import Assembler, Part

    assembler = Assembler(DIMENSION_DATA)
    assembly_parts = [Part.BOTTOM, Part.LONG_SIDE, Part.SHORT_SIDE]
    # assembly = assembler.assemble(assembly_parts)
    assembly = assembler.assemble()
    show_object(assembly, name="Garbage Sort Box Assembly")  # type: ignore


def show_generic_box():
    from primitives.plywood_box.project_data import Part
    from primitives.plywood_box.assembly import Assembler
    from projects.generic_box import BOX_DIMENSIONS

    part_types = [Part.BOTTOM, Part.LONG_SIDE, Part.SHORT_SIDE, Part.TOP]
    # part_types = list(Part)
    visual_offset = 0
    assembly = Assembler.get_assembly(BOX_DIMENSIONS, visual_offset=visual_offset, assembly_parts=part_types)
    show_object(assembly, name="Generic box")  # type: ignore

def show_generic_box_part():
    from primitives.plywood_box.project_data import PartType
    from primitives.plywood_box.parts import Builder
    from projects.generic_box import BOX_DIMENSIONS

    part_type = PartType.LONG_SIDE_PANEL
    part = Builder.get_part(BOX_DIMENSIONS, part_type)
    show_object(part, name=part_type.name.replace("_", " ").capitalize())




show_garbage_sort_box()
# show_generic_box_part()
# show_generic_box()
