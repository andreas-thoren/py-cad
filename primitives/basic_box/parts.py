import cadquery as cq
from helpers.models import BuilderABC, DimensionData
from .project_data import PartType


class Builder(BuilderABC):
    part_types = PartType

    top_divider_y = 300
    top_divider_z = 300

    def __init__(self, dim: DimensionData):
        super().__init__(dim)
        # Calculated dimensions
        offset_x = (
            self.dim.material_thickness[PartType.SHORT_SIDE_PANEL]
            - self.dim.route_depth
        )
        offset_y = (
            self.dim.material_thickness[PartType.LONG_SIDE_PANEL] - self.dim.route_depth
        )
        offset_z = self.dim.material_thickness[PartType.TOP] - self.dim.route_depth
        self.bottom_x = self.dim.x_len - 2 * offset_x
        self.panel_y = self.dim.y_len - 2 * offset_y
        self.panel_z = self.dim.z_len - offset_z

    @BuilderABC.register(PartType.LONG_SIDE_PANEL)
    def get_long_side_panel(self) -> cq.Workplane:
        thickness = self.dim.material_thickness[PartType.LONG_SIDE_PANEL]
        bottom_thickness = self.dim.material_thickness[PartType.BOTTOM]
        side_groove_offset = self.dim.x_len / 2 - thickness / 2

        return (
            cq.Workplane("XZ")
            .box(self.dim.x_len, self.panel_z, thickness)
            .faces("<Y")
            .workplane()
            .pushPoints([(side_groove_offset, 0), (-side_groove_offset, 0)])
            .rect(thickness, self.panel_z)
            .cutBlind(-self.dim.route_depth)
            .faces("<Y")
            .workplane()
            .moveTo(0, -(self.panel_z - bottom_thickness) / 2)
            .rect(self.dim.x_len, bottom_thickness)
            .cutBlind(-self.dim.route_depth)
        )

    @BuilderABC.register(PartType.SHORT_SIDE_PANEL)
    def get_short_side_panel(self) -> cq.Workplane:
        thickness = self.dim.material_thickness[PartType.SHORT_SIDE_PANEL]
        bottom_thickness = self.dim.material_thickness[PartType.BOTTOM]

        return (
            cq.Workplane("YZ")
            .box(self.panel_y, self.panel_z, thickness)
            .faces("<X")
            .workplane()
            .moveTo(0, -(self.panel_z - bottom_thickness) / 2)
            .rect(self.panel_y, bottom_thickness)
            .cutBlind(-self.dim.route_depth)
        )

    @BuilderABC.register(PartType.BOTTOM)
    def get_bottom(self) -> cq.Workplane:
        thickness = self.dim.material_thickness[PartType.BOTTOM]
        return cq.Workplane("XY").box(self.bottom_x, self.panel_y, thickness)

    @BuilderABC.register(PartType.TOP)
    def get_top(self) -> cq.Workplane:
        thickness = self.dim.material_thickness[PartType.TOP]
        return (
            cq.Workplane("XY")
            .box(self.dim.x_len, self.dim.y_len, thickness - self.dim.route_depth)
            .faces(">Z")
            .workplane()
            .rect(
                self.dim.x_len - thickness * 2,
                self.dim.y_len - thickness * 2,
            )
            .extrude(self.dim.route_depth)
        )
