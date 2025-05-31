def get_garbage_sort_box():
    from projects.garbage_sort_box.project_data import DIMENSION_DATA
    from projects.garbage_sort_box.assembly import Assembler, Part

    assembler = Assembler(DIMENSION_DATA)
    assembly_parts = [Part.BOTTOM, Part.LONG_SIDE, Part.SHORT_SIDE]
    # assembly = assembler.assemble(assembly_parts)
    assembly = assembler.assemble()
    return assembly, "Garbage Sort Box Assembly"


def get_plywood_box():
    from primitives.plywood_box.project_data import Part
    from primitives.plywood_box.assembly import Assembler
    from projects.generic_plywood_box import BOX_DIMENSIONS

    part_types = [Part.BOTTOM, Part.LONG_SIDE, Part.SHORT_SIDE, Part.TOP]
    # part_types = list(Part)
    visual_offset = 0
    assembly = Assembler.get_assembly(
        BOX_DIMENSIONS, visual_offset=visual_offset, assembly_parts=part_types
    )
    return assembly, "Generic box"


def get_plywood_box_part():
    from primitives.plywood_box.project_data import PartType
    from primitives.plywood_box.parts import Builder
    from projects.generic_plywood_box import BOX_DIMENSIONS

    part_type = PartType.LONG_SIDE_PANEL
    part = Builder.get_part(BOX_DIMENSIONS, part_type)
    return part, part_type.name.replace("_", " ").capitalize()


def get_basic_box():
    from primitives.basic_box.project_data import Part
    from primitives.basic_box.assembly import Assembler
    from projects.generic_box import BOX_DIMENSIONS

    # part_types = [Part.BOTTOM, Part.LONG_SIDE, Part.LONG_SIDE_INVERSE, Part.SHORT_SIDE_INVERSE, Part.TOP]
    part_types = list(Part)
    # print(part_types)
    visual_offset = 0
    assembly = Assembler.get_assembly(
        BOX_DIMENSIONS, visual_offset=visual_offset, assembly_parts=part_types
    )
    return assembly, "Basic box"


def get_basic_box_part():
    from primitives.basic_box.project_data import PartType
    from primitives.basic_box.parts import Builder
    from projects.generic_box import BOX_DIMENSIONS

    part_type = PartType.TOP
    part = Builder.get_part(BOX_DIMENSIONS, part_type)
    return part, part_type.name.replace("_", " ").capitalize()


def get_test_project():
    from tests.test_project.project_data import DIMENSION_DATA, Part
    from tests.test_project.assembly import PartialAssemblerOuterLeaf

    assembler = PartialAssemblerOuterLeaf(DIMENSION_DATA)
    # assembly_parts = [Part.BOTTOM, Part.LONG_SIDE, Part.SHORT_SIDE]
    # assembly = assembler.assemble(assembly_parts)
    assembly = assembler.assemble()
    return assembly, "Garbage Sort Box Assembly"


# assembly, name = get_garbage_sort_box()
assembly, name = get_test_project()
# assembly, name = get_plywood_box_part()
# assembly, name = get_plywood_box()
# assembly, name = get_basic_box()
# assembly, name = get_basic_box_part()

show_object(assembly, name)
