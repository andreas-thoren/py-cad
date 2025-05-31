from enum import auto
from helpers.models import StrAutoEnum, DimensionData

# Project dimensions
BOX_X = 490
BOX_Y = 350
BOX_Z = 540


class Part(StrAutoEnum):
    BOTTOM = auto()
    LONG_SIDE = auto()
    LONG_SIDE_INVERSE = auto()
    SHORT_SIDE = auto()
    SHORT_SIDE_INVERSE = auto()
    TOP = auto()


class PartType(StrAutoEnum):
    BOTTOM = auto()
    LONG_SIDE_PANEL = auto()
    SHORT_SIDE_PANEL = auto()
    TOP = auto()


PART_TYPE_MAP = {
    Part.BOTTOM: PartType.BOTTOM,
    Part.LONG_SIDE: PartType.LONG_SIDE_PANEL,
    Part.LONG_SIDE_INVERSE: PartType.LONG_SIDE_PANEL,
    Part.SHORT_SIDE: PartType.SHORT_SIDE_PANEL,
    Part.SHORT_SIDE_INVERSE: PartType.SHORT_SIDE_PANEL,
    Part.TOP: PartType.TOP,
}


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


class BoxDimensionData(DimensionData):
    def __init__(
        self,
        x_len: float,
        y_len: float,
        z_len: float,
        mat_thickness: dict[PartType, float],
        route_depth: float = 0.0,
    ):
        part_type_attributes = {"mat_thickness": mat_thickness}
        super().__init__((x_len, y_len, z_len), part_type_attributes)
        self.route_depth = route_depth
        self.routed_x_len = mat_thickness[PartType.SHORT_SIDE_PANEL] - route_depth
        self.routed_y_len = mat_thickness[PartType.LONG_SIDE_PANEL] - route_depth
        self.routed_z_len = mat_thickness[PartType.TOP] - route_depth
        self.panel_z_len = z_len - self.routed_z_len

    def get_part_types_dimensions(self):
        panel_y = self.y_len - 2 * self.routed_y_len
        btm_x = self.x_len - 2 * self.routed_x_len
        btm_z = self[PartType.BOTTOM].mat_thickness
        top_z = self[PartType.TOP].mat_thickness
        long_panel_thickness = self[PartType.LONG_SIDE_PANEL].mat_thickness
        short_panel_thickness = self[PartType.SHORT_SIDE_PANEL].mat_thickness

        return {
            PartType.BOTTOM: (btm_x, panel_y, btm_z),
            PartType.LONG_SIDE_PANEL: (
                self.x_len,
                long_panel_thickness,
                self.panel_z_len,
            ),
            PartType.SHORT_SIDE_PANEL: (
                short_panel_thickness,
                panel_y,
                self.panel_z_len,
            ),
            PartType.TOP: (self.x_len, self.y_len, top_z),
        }


DIMENSION_DATA = BoxDimensionData(
    BOX_X, BOX_Y, BOX_Z, PART_TYPE_THICKNESS_MAP, route_depth=ROUTE_DEPTH
)
