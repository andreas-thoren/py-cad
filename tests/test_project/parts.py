import cadquery as cq
from helpers.models import BuilderABC, DimensionData
from .project_data import PartType


class PartialBuilderBase(BuilderABC):
    part_types = [PartType.BOTTOM]

    top_divider_y = 300
    top_divider_z = 300

    def __init__(self, dim: DimensionData):
        super().__init__(dim)
        # Calculated dimensions
        self.top_divider_x = self.dim.x_len - self.dim.mat_thickness
        self.route_depth = self.dim.mat_thickness / 2
        self.offset = self.dim.mat_thickness - self.route_depth
        self.panel_y = self.dim.y_len - 2 * self.offset
        self.panel_z = self.dim.z_len - self.offset

    @BuilderABC.register(PartType.BOTTOM)
    def get_bottom_panel(self) -> cq.Workplane:
        return (
            cq.Workplane("XY")
            .box(
                self.dim.x_len, self.dim.y_len, self.dim.mat_thickness - self.route_depth
            )
            .faces(">Z")
            .workplane()
            .rect(
                self.dim.x_len - self.dim.mat_thickness * 2,
                self.dim.y_len - self.dim.mat_thickness * 2,
            )
            .extrude(self.route_depth)
        )


class PartialBuilderMid(PartialBuilderBase):
    part_types = [PartType.LONG_SIDE_PANEL]

    @BuilderABC.register(PartType.LONG_SIDE_PANEL)
    def get_long_side_panel(self, invert_grooves=False) -> cq.Workplane:
        groove_offset = self.dim.x_len / 2 - self.dim.mat_thickness / 2
        groove_face = ">Y" if invert_grooves else "<Y"
        divider_width = 50

        return (
            cq.Workplane("XZ")
            .box(self.dim.x_len, self.panel_z, self.dim.mat_thickness)
            .faces(groove_face)
            .workplane()
            .pushPoints([(groove_offset, 0), (-groove_offset, 0)])
            .rect(self.dim.mat_thickness, self.panel_z)
            .cutBlind(-self.route_depth)
            .faces(groove_face)
            .workplane()
            .moveTo(0, (self.panel_z - divider_width) / 2)
            .rect(self.dim.mat_thickness, divider_width)
            .cutBlind(-self.route_depth)
        )


class PartialBuilderLeaf(PartialBuilderMid):
    part_types = [PartType.SHORT_SIDE_PANEL]

    @BuilderABC.register(PartType.SHORT_SIDE_PANEL)
    def get_short_side_panel(self) -> cq.Workplane:
        return cq.Workplane("YZ").box(
            self.panel_y, self.panel_z, self.dim.mat_thickness
        )
