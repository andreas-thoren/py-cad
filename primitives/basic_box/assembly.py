import cadquery as cq
from helpers.models import AssemblerABC, DimensionData
from .parts import Builder
from .project_data import Part, PartType, PART_TYPE_MAP


class Assembler(AssemblerABC):
    BuilderClass = Builder
    parts = Part
    part_map = PART_TYPE_MAP

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        dim: DimensionData,
        visual_offset: int = 0,
    ):
        super().__init__(dim)
        x_thickness = self.material_thickness[PartType.SHORT_SIDE_PANEL]
        y_thickness = self.material_thickness[PartType.LONG_SIDE_PANEL]
        bottom_thickness = self.material_thickness[PartType.BOTTOM]
        top_thickness = self.material_thickness[PartType.TOP]
        panel_z = self.z_length - (top_thickness - self.route_depth)

        self.x_offset = visual_offset + (self.x_length - x_thickness) / 2
        self.y_offset = visual_offset + (self.y_length - y_thickness) / 2
        self.bottom_offset = (panel_z - bottom_thickness) / 2
        self.top_offset = visual_offset + self.z_length / 2

    def get_metadata_map(self) -> dict[Part, dict]:
        # pylint: disable=no-value-for-parameter, too-many-function-args
        return {
            Part.BOTTOM: {
                "loc": cq.Location((0, 0, -self.bottom_offset)),
                "name": "Bottom Panel",
                "color": cq.Color("burlywood"),
            },
            Part.LONG_SIDE: {
                "loc": cq.Location((0, self.y_offset, 0)),
                "name": "Long side panel",
                "color": cq.Color("burlywood2"),
            },
            Part.LONG_SIDE_INVERSE: {
                "loc": cq.Location((0, -self.y_offset, 0), (0, 0, 1), 180),
                "name": "Long side panel inverse",
                "color": cq.Color("burlywood2"),
            },
            Part.SHORT_SIDE: {
                "loc": cq.Location((self.x_offset, 0, 0)),
                "name": "Short side panel",
                "color": cq.Color("burlywood4"),
            },
            Part.SHORT_SIDE_INVERSE: {
                "loc": cq.Location((-self.x_offset, 0, 0), (0, 0, 1), 180),
                "name": "Short side panel inverse",
                "color": cq.Color("burlywood4"),
            },
            Part.TOP: {
                "loc": cq.Location((0, 0, self.top_offset), (1, 0, 0), 180),
                "name": "Top Panel",
                "color": cq.Color("burlywood"),
            },
        }
