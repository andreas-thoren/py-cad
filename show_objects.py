def show_garbage_sort_box():
    from projects.garbage_sort_box.assembly import Assembler, PartType

    assembly = Assembler(
        [PartType.BOTTOM, PartType.LONG_SIDE, PartType.SHORT_SIDE]
    ).assemble()
    # assembly = Assembler().assemble()
    show_object(assembly, name="Garbage Sort Box Assembly")  # type: ignore


def show_generic_box():
    pass


show_garbage_sort_box()
