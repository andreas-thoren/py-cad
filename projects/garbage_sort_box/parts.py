from enum import Enum, auto
import cadquery as cq
from helpers.models import BuilderABC, DimensionData


class Part(Enum):
    BOTTOM = auto()
    LONG_SIDE = auto()
    LONG_SIDE_INVERSE = auto()
    SHORT_SIDE = auto()
    SHORT_SIDE_INVERSE = auto()


class Builder(BuilderABC):
    _PartEnum = Part

    top_divider_y = 300
    top_divider_z = 300

    def __init__(self, dimension_data: DimensionData):
        super().__init__(dimension_data)
        # Calculated dimensions
        self.top_divider_x = self.x_length - self.material_thickness
        self.route_depth = self.material_thickness / 2
        self.offset = self.material_thickness - self.route_depth
        self.panel_y = self.y_length - 2 * self.offset
        self.panel_z = self.z_length - self.offset

    @BuilderABC.register(Part.LONG_SIDE, Part.LONG_SIDE_INVERSE)
    def get_long_side_panel(self, invert_grooves=False) -> cq.Workplane:
        groove_offset = self.x_length / 2 - self.material_thickness / 2
        groove_face = ">Y" if invert_grooves else "<Y"
        divider_width = 50

        return (
            cq.Workplane("XZ")
            .box(self.x_length, self.panel_z, self.material_thickness)
            .faces(groove_face)
            .workplane()
            .pushPoints([(groove_offset, 0), (-groove_offset, 0)])
            .rect(self.material_thickness, self.panel_z)
            .cutBlind(-self.route_depth)
            .faces(groove_face)
            .workplane()
            .moveTo(0, (self.panel_z - divider_width) / 2)
            .rect(self.material_thickness, divider_width)
            .cutBlind(-self.route_depth)
        )

    @BuilderABC.register(Part.BOTTOM)
    def get_bottom_panel(self) -> cq.Workplane:
        return (
            cq.Workplane("XY")
            .box(
                self.x_length, self.y_length, self.material_thickness - self.route_depth
            )
            .faces(">Z")
            .workplane()
            .rect(
                self.x_length - self.material_thickness * 2,
                self.y_length - self.material_thickness * 2,
            )
            .extrude(self.route_depth)
        )

    @BuilderABC.register(Part.SHORT_SIDE, Part.SHORT_SIDE_INVERSE)
    def get_short_side_panel(self) -> cq.Workplane:
        return cq.Workplane("YZ").box(
            self.panel_y, self.panel_z, self.material_thickness
        )
