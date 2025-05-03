from parts import PartType
from assembly import Assembler

# pylint: disable=undefined-variable

# assembly = Assembler([PartType.BOTTOM, PartType.LONG_SIDE, PartType.SHORT_SIDE]).assemble()
assembly = Assembler().assemble()
show_object(assembly, name="Garbage Sort Box Assembly")  # type: ignore
