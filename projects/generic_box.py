from enum import auto
from py_cad import StrAutoEnum
from py_cad.primitives.basic_box.project_data import BoxDimensionData, PartType

# Basic dimensions
BOX_X = 400
BOX_Y = 200
BOX_Z = 200


# Materials
class Material(StrAutoEnum):
    PLYWOOD = auto()
    SOLID_WOOD = auto()


# Material thicknesses map
MATERIAL_THICKNESS_MAP = {
    Material.PLYWOOD: 9,
    Material.SOLID_WOOD: 12,
}

# Part type materials
PART_TYPE_MATERIAL_MAP = {
    PartType.BOTTOM: Material.PLYWOOD,
    PartType.LONG_SIDE_PANEL: Material.SOLID_WOOD,
    PartType.SHORT_SIDE_PANEL: Material.SOLID_WOOD,
    PartType.TOP: Material.SOLID_WOOD,
}

# Part type thicknesses
PART_TYPE_THICKNESS_MAP = {
    part_type: MATERIAL_THICKNESS_MAP[material]
    for part_type, material in PART_TYPE_MATERIAL_MAP.items()
}

# Route depth
ROUTE_DEPTH = MATERIAL_THICKNESS_MAP[Material.SOLID_WOOD] / 2

# Box dimensions
BOX_DIMENSIONS = BoxDimensionData(
    BOX_X, BOX_Y, BOX_Z, PART_TYPE_THICKNESS_MAP, route_depth=ROUTE_DEPTH
)
