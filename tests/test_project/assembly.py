import cadquery as cq
from helpers.models import AssemblerABC, DimensionData
from .parts import PartialBuilderLeaf, PartialBuilderMid, PartialBuilderBase
from .project_data import Part, PartType


class PartialAssemblerBase(AssemblerABC):
    BuilderClass = PartialBuilderBase
    part_map = {
        Part.BOTTOM: PartType.BOTTOM,
    }

    def __init__(self, dim: DimensionData):
        super().__init__(dim)
        self.x_offset = (self.dim.x_len - self.dim.mat_thickness) / 2
        self.y_offset = (self.dim.y_len - self.dim.mat_thickness) / 2
        self.z_offset = self.dim.z_len / 2

    def get_metadata_map(self) -> dict[Part, dict]:
        # pylint: disable=no-value-for-parameter, too-many-function-args
        return {
            Part.BOTTOM: {
                "loc": cq.Location((0, 0, 0)),
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
                "loc": cq.Location((0, self.y_offset, self.z_offset)),
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
                "loc": cq.Location((0, -self.y_offset, self.z_offset), (0, 0, 1), 180),
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
