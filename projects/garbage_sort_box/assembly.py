import cadquery as cq
from helpers.models import AssemblerABC, DimensionData
from .parts import Builder
from .project_data import Part, PART_TYPE_MAP


class Assembler(AssemblerABC):
    BuilderClass = Builder
    parts = Part
    part_map = PART_TYPE_MAP.copy()

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        dimension_data: DimensionData,
        visual_offset: int = 0,
    ):
        super().__init__(dimension_data)
        self.x_offset = visual_offset + (self.x_length - self.material_thickness) / 2
        self.y_offset = visual_offset + (self.y_length - self.material_thickness) / 2
        self.z_offset = self.z_length / 2

    def get_metadata_map(self) -> dict[Part, dict]:
        # pylint: disable=no-value-for-parameter, too-many-function-args
        return {
            Part.BOTTOM: {
                "loc": cq.Location((0, 0, 0)),
                "name": "Bottom Panel",
                "color": cq.Color("burlywood"),
            },
            Part.LONG_SIDE: {
                "loc": cq.Location((0, self.y_offset, self.z_offset)),
                "name": "Long side panel",
                "color": cq.Color("burlywood2"),
            },
            Part.LONG_SIDE_INVERSE: {
                "loc": cq.Location((0, -self.y_offset, self.z_offset), (0, 0, 1), 180),
                "name": "Long side panel inverse",
                "color": cq.Color("burlywood2"),
            },
            Part.SHORT_SIDE: {
                "loc": cq.Location((self.x_offset, 0, self.z_offset)),
                "name": "Short side panel",
                "color": cq.Color("burlywood4"),
            },
            Part.SHORT_SIDE_INVERSE: {
                "loc": cq.Location((-self.x_offset, 0, self.z_offset)),
                "name": "Short side panel inverse",
                "color": cq.Color("burlywood4"),
            },
        }
