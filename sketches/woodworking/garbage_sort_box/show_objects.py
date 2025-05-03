from parts import Part
from assembly import Assembler

# pylint: disable=undefined-variable

# assembly = Assembler([Part.BOTTOM, Part.LONG_SIDE, Part.SHORT_SIDE]).assemble()
assembly = Assembler().assemble()
show_object(assembly, name="Garbage Sort Box Assembly")  # type: ignore
