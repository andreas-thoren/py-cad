from primitives.plywood_box.assembly import Assembler
from primitives.plywood_box.parts import Builder, PartType
from projects.generic_plywood_box import BOX_DIMENSIONS

# part = Builder.get_part(BOX_DIMENSIONS, Part.BOTTOM)
assembly = Assembler.get_assembly(BOX_DIMENSIONS)
