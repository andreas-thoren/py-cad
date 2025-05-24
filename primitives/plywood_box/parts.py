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
        self.top_divider_x = self.dim.x_len - self.dim.material_thickness
        self.offset = self.dim.material_thickness - self.dim.route_depth
        self.panel_y = self.dim.y_len - 2 * self.offset
        self.panel_z = self.dim.z_len - 2 * self.offset

    @BuilderABC.register(PartType.LONG_SIDE_PANEL)
    def get_long_side_panel(self, invert_grooves=False) -> cq.Workplane:
        groove_offset = self.dim.x_len / 2 - self.dim.material_thickness / 2
        groove_face = ">Y" if invert_grooves else "<Y"

        return (
            cq.Workplane("XZ")
            .box(self.dim.x_len, self.panel_z, self.dim.material_thickness)
            .faces(groove_face)
            .workplane()
            .pushPoints([(groove_offset, 0), (-groove_offset, 0)])
            .rect(self.dim.material_thickness, self.panel_z)
            .cutBlind(-self.dim.route_depth)
        )

    @BuilderABC.register(PartType.BOTTOM)
    def get_bottom_panel(self) -> cq.Workplane:
        return (
            cq.Workplane("XY")
            .box(
                self.dim.x_len, self.dim.y_len, self.dim.material_thickness - self.dim.route_depth
            )
            .faces(">Z")
            .workplane()
            .rect(
                self.dim.x_len - self.dim.material_thickness * 2,
                self.dim.y_len - self.dim.material_thickness * 2,
            )
            .extrude(self.dim.route_depth)
        )

    @BuilderABC.register(PartType.SHORT_SIDE_PANEL)
    def get_short_side_panel(self) -> cq.Workplane:
        return cq.Workplane("YZ").box(
            self.panel_y, self.panel_z, self.dim.material_thickness
        )
