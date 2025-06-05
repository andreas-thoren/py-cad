import cadquery as cq
from py_cad import AssemblerABC, DimensionData
from .parts import (
    PartialBuilderLeaf,
    PartialBuilderMid,
    PartialBuilderBase,
    PartialBuilderOuterLeaf,
)
from .project_data import Part, PartType


class PartialAssemblerBase(AssemblerABC):
    BuilderClass = PartialBuilderBase
    part_map = {
        Part.BOTTOM: PartType.BOTTOM,
    }

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
        }


class PartialAssemblerMidOne(PartialAssemblerBase):
    BuilderClass = PartialBuilderMid
    part_map = {
        Part.LONG_SIDE: PartType.LONG_SIDE_PANEL,
    }

    def get_metadata_map(self) -> dict[Part, dict]:
        return {
            # pylint: disable=no-value-for-parameter
            Part.LONG_SIDE: {
                "loc": cq.Location((0, self.assy_dst_y, 0)),
                "name": "Long side panel",
                "color": cq.Color("burlywood2"),
            },
        }


class PartialAssemblerMidTwo(PartialAssemblerBase):
    BuilderClass = PartialBuilderMid
    part_map = {
        Part.LONG_SIDE_INVERSE: PartType.LONG_SIDE_PANEL,
    }

    def get_metadata_map(self) -> dict[Part, dict]:
        return {
            # pylint: disable=no-value-for-parameter, too-many-function-args
            Part.LONG_SIDE_INVERSE: {
                "loc": cq.Location((0, -self.assy_dst_y, 0), (0, 0, 1), 180),
                "name": "Long side panel inverse",
                "color": cq.Color("burlywood2"),
            },
        }


class PartialAssemblerLeaf(PartialAssemblerMidOne, PartialAssemblerMidTwo):
    BuilderClass = PartialBuilderLeaf
    part_map = {
        Part.SHORT_SIDE: PartType.SHORT_SIDE_PANEL,
        Part.SHORT_SIDE_INVERSE: PartType.SHORT_SIDE_PANEL,
    }

    def get_metadata_map(self) -> dict[Part, dict]:
        # pylint: disable=no-value-for-parameter, too-many-function-args
        return {
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
        }


class PartialAssemblerOuterLeaf(PartialAssemblerLeaf):
    BuilderClass = PartialBuilderOuterLeaf
    # Testing implicit mapping of PartType.TOP

    def get_metadata_map(self) -> dict[Part, dict]:
        # pylint: disable=no-value-for-parameter, too-many-function-args
        return {
            Part.TOP: {
                "loc": cq.Location((0, 0, self.assy_dst_top), (1, 0, 0), 180),
                "name": "Top Panel",
                "color": cq.Color("burlywood"),
            },
        }
