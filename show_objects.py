from helpers.models import DimensionData

def show_garbage_sort_box():
    import projects.garbage_sort_box.measurements as m
    from projects.garbage_sort_box.assembly import Assembler, PartType

    dimension_data = DimensionData(m.BOX_X, m.BOX_Y, m.BOX_Z, m.PLY_THICKNESS)
    assembler = Assembler(dimension_data)
    assembly_parts = [PartType.BOTTOM, PartType.LONG_SIDE, PartType.SHORT_SIDE]
    assembly = assembler.assemble(assembly_parts)
    # assembly = assembler.assemble()
    show_object(assembly, name="Garbage Sort Box Assembly")  # type: ignore


def show_generic_box():
    from projects.generic_box import generic_box
    # show_object(generic_box, name="Generic box")  # type: ignore


show_garbage_sort_box()
# show_generic_box()
