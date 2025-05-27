from enum import StrEnum
from helpers.models import BasicDimensionData, DimensionData


class Part(StrEnum):
    BOTTOM = "bottom"
    LONG_SIDE = "long side"
    LONG_SIDE_INVERSE = "long side inverse"
    SHORT_SIDE = "short side"
    SHORT_SIDE_INVERSE = "short side inverse"
    TOP = "top"


class PartType(StrEnum):
    BOTTOM = "bottom"
    LONG_SIDE_PANEL = "long side panel"
    SHORT_SIDE_PANEL = "short side panel"
    TOP = "top"


PART_TYPE_MAP = {
    Part.BOTTOM: PartType.BOTTOM,
    Part.LONG_SIDE: PartType.LONG_SIDE_PANEL,
    Part.LONG_SIDE_INVERSE: PartType.LONG_SIDE_PANEL,
    Part.SHORT_SIDE: PartType.SHORT_SIDE_PANEL,
    Part.SHORT_SIDE_INVERSE: PartType.SHORT_SIDE_PANEL,
    Part.TOP: PartType.TOP,
}


class BoxDimensionData(DimensionData):
    def __init__(
        self,
        x_len: float,
        y_len: float,
        z_len: float,
        mat_thickness: dict[PartType, float],
        route_depth: float = 0.0,
    ):
        self.route_depth = route_depth
        self.routed_x_len = mat_thickness[PartType.SHORT_SIDE_PANEL] - route_depth
        self.routed_y_len = mat_thickness[PartType.LONG_SIDE_PANEL] - route_depth
        self.routed_z_len = mat_thickness[PartType.TOP] - route_depth
        self.panel_z_len = z_len - self.routed_z_len
        # Should be called last so that get_part_types_dimensions can access attributes above
        super().__init__(x_len, y_len, z_len, mat_thickness)

    def get_part_types_dimensions(self) -> dict[PartType, BasicDimensionData]:
        panel_y = self.y_len - 2 * self.routed_y_len

        btm_x = self.x_len - 2 * self.routed_x_len
        btm_z = self.get_part_type_thickness(PartType.BOTTOM)
        top_z = self.get_part_type_thickness(PartType.TOP)
        long_panel_thickness = self.get_part_type_thickness(PartType.LONG_SIDE_PANEL)
        short_panel_thickness = self.get_part_type_thickness(PartType.SHORT_SIDE_PANEL)

        return {
            PartType.BOTTOM: BasicDimensionData(btm_x, panel_y, btm_z),
            PartType.LONG_SIDE_PANEL: BasicDimensionData(
                self.x_len, long_panel_thickness, self.panel_z_len
            ),
            PartType.SHORT_SIDE_PANEL: BasicDimensionData(
                short_panel_thickness, panel_y, self.panel_z_len
            ),
            PartType.TOP: BasicDimensionData(self.x_len, self.y_len, top_z),
        }
