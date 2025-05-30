import cadquery as cq
from helpers.models import AssemblerABC, DimensionData
from .parts import Builder
from .project_data import Part, PartType, PART_TYPE_MAP


class Assembler(AssemblerABC):
    BuilderClass = Builder
    part_map = PART_TYPE_MAP

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        dim: DimensionData,
        visual_offset: int = 0,
    ):
        super().__init__(dim)
        btm_z = self.dim[PartType.BOTTOM].z_len

        self.assy_dst_x = (self.dim.x_len / 2) + visual_offset - self.dim.routed_x_len
        self.assy_dst_y = (self.dim.y_len / 2) + visual_offset - self.dim.routed_y_len
        self.assy_dst_bottom = (self.dim.panel_z_len - btm_z) / 2
        self.assy_dst_top = visual_offset + self.dim.z_len / 2

    def get_metadata_map(self) -> dict[Part, dict]:
        # pylint: disable=no-value-for-parameter, too-many-function-args
        return {
            Part.BOTTOM: {
                "loc": cq.Location((0, 0, -self.assy_dst_bottom)),
                "name": "Bottom Panel",
                "color": cq.Color("burlywood"),
            },
            Part.LONG_SIDE: {
                "loc": cq.Location((0, self.assy_dst_y, 0)),
                "name": "Long side panel",
                "color": cq.Color("burlywood2"),
            },
            Part.LONG_SIDE_INVERSE: {
                "loc": cq.Location((0, -self.assy_dst_y, 0), (0, 0, 1), 180),
                "name": "Long side panel inverse",
                "color": cq.Color("burlywood2"),
            },
            Part.SHORT_SIDE: {
                "loc": cq.Location((self.assy_dst_x, 0, 0)),
                "name": "Short side panel",
                "color": cq.Color("burlywood4"),
            },
            Part.SHORT_SIDE_INVERSE: {
                "loc": cq.Location((-self.assy_dst_x, 0, 0), (0, 0, 1), 180),
                "name": "Short side panel inverse",
                "color": cq.Color("burlywood4"),
            },
            Part.TOP: {
                "loc": cq.Location((0, 0, self.assy_dst_top), (1, 0, 0), 180),
                "name": "Top Panel",
                "color": cq.Color("burlywood"),
            },
        }
