from py_cad import DimensionData
from py_cad.primitives.plywood_box.assembly import Assembler, Part
from py_cad.primitives.plywood_box.parts import Builder, PartType

PLY_THICKNESS = 9
BOX_DIMENSIONS = DimensionData(
    (300, 200, 200), mat_thickness=PLY_THICKNESS, route_depth=PLY_THICKNESS / 2
)

# part = Builder.get_part(BOX_DIMENSIONS, Part.BOTTOM)
assembly = Assembler.get_assembly(BOX_DIMENSIONS)
