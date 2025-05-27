from enum import StrEnum
from helpers.models import DimensionData


class Part(StrEnum):
    BOTTOM = "bottom"
    LONG_SIDE = "long side"
    LONG_SIDE_INVERSE = "long side inverse"
    SHORT_SIDE = "short side"
    SHORT_SIDE_INVERSE = "short side inverse"


class PartType(StrEnum):
    BOTTOM = "bottom"
    LONG_SIDE_PANEL = "long side panel"
    SHORT_SIDE_PANEL = "short side panel"


PART_TYPE_MAP = {
    Part.BOTTOM: PartType.BOTTOM,
    Part.LONG_SIDE: PartType.LONG_SIDE_PANEL,
    Part.LONG_SIDE_INVERSE: PartType.LONG_SIDE_PANEL,
    Part.SHORT_SIDE: PartType.SHORT_SIDE_PANEL,
    Part.SHORT_SIDE_INVERSE: PartType.SHORT_SIDE_PANEL,
}


# Project dimensions
BOX_X = 490
BOX_Y = 350
BOX_Z = 540
PLY_THICKNESS = 9

DIMENSION_DATA = DimensionData(BOX_X, BOX_Y, BOX_Z, mat_thickness=PLY_THICKNESS)
