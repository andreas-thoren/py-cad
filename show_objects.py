def show_garbage_sort_box():
    from projects.garbage_sort_box.assembly import Assembler, PartType

    assembly_parts = [PartType.BOTTOM, PartType.LONG_SIDE, PartType.SHORT_SIDE]
    assembly = Assembler().assemble(assembly_parts)
    # assembly = Assembler().assemble()
    show_object(assembly, name="Garbage Sort Box Assembly")  # type: ignore


def show_generic_box():
    from projects.generic_box import generic_box

    show_object(generic_box, name="Generic box")  # type: ignore


show_garbage_sort_box()
# show_generic_box()
