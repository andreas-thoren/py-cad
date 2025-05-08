from primitives.basic_box.assembly import Assembler
from primitives.basic_box.parts import Builder, PartType
from projects.generic_box import BOX_DIMENSIONS

# part = Builder.get_part(BOX_DIMENSIONS, PartType.BOTTOM)
assembly = Assembler.get_assembly(BOX_DIMENSIONS)
