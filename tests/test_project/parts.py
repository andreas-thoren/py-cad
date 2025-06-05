import cadquery as cq
from py_cad import BuilderABC
from .project_data import PartType


class PartialBuilderBase(BuilderABC):
    top_divider_y = 300
    top_divider_z = 300

    @BuilderABC.register(PartType.BOTTOM)
    def get_bottom(self) -> cq.Workplane:
        btm = self.dim[PartType.BOTTOM]
        return cq.Workplane("XY").box(btm.x_len, btm.y_len, btm.z_len)


class PartialBuilderMid(PartialBuilderBase):
    @BuilderABC.register(PartType.LONG_SIDE_PANEL)
    def get_long_side_panel(self) -> cq.Workplane:
        long = self.dim[PartType.LONG_SIDE_PANEL]
        bottom_thickness = self.dim[PartType.BOTTOM].z_len
        side_groove_offset = self.dim.x_len / 2 - long.y_len / 2

        return (
            cq.Workplane("XY")
            .box(long.x_len, long.y_len, long.z_len)
            .faces("<Y")
            .workplane()
            .pushPoints([(side_groove_offset, 0), (-side_groove_offset, 0)])
            .rect(long.y_len, long.z_len)
            .cutBlind(-self.dim.route_depth)
            .faces("<Y")
            .workplane()
            .moveTo(0, -(long.z_len - bottom_thickness) / 2)
            .rect(self.dim.x_len, bottom_thickness)
            .cutBlind(-self.dim.route_depth)
        )


class PartialBuilderLeaf(PartialBuilderMid):
    @BuilderABC.register(PartType.SHORT_SIDE_PANEL)
    def get_short_side_panel(self) -> cq.Workplane:
        short = self.dim[PartType.SHORT_SIDE_PANEL]
        bottom_thickness = self.dim[PartType.BOTTOM].z_len

        return (
            cq.Workplane("XY")
            .box(short.x_len, short.y_len, short.z_len)
            .faces("<X")
            .workplane()
            .moveTo(0, -(short.z_len - bottom_thickness) / 2)
            .rect(short.y_len, bottom_thickness)
            .cutBlind(-self.dim.route_depth)
        )


class PartialBuilderOuterLeaf(PartialBuilderLeaf):
    @BuilderABC.register(PartType.TOP)
    def get_top(self) -> cq.Workplane:
        top = self.dim[PartType.TOP]
        return (
            cq.Workplane("XY")
            .box(self.dim.x_len, self.dim.y_len, top.z_len - self.dim.route_depth)
            .faces(">Z")
            .workplane()
            .rect(
                self.dim.x_len - top.z_len * 2,
                self.dim.y_len - top.z_len * 2,
            )
            .extrude(self.dim.route_depth)
        )
