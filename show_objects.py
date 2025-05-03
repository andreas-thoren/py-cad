from sketches.garbage_sort_box.parts import PartType
from sketches.garbage_sort_box.assembly import Assembler

# pylint: disable=undefined-variable

# assembly = Assembler([PartType.BOTTOM, PartType.LONG_SIDE, PartType.SHORT_SIDE]).assemble()
assembly = Assembler().assemble()
show_object(assembly, name="Garbage Sort Box Assembly")  # type: ignore
