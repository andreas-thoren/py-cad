from enum import auto
from py_cad import StrAutoEnum, DimensionData


class Part(StrAutoEnum):
    BOTTOM = auto()
    LONG_SIDE = auto()
    LONG_SIDE_INVERSE = auto()
    SHORT_SIDE = auto()
    SHORT_SIDE_INVERSE = auto()


class PartType(StrAutoEnum):
    BOTTOM = auto()
    LONG_SIDE_PANEL = auto()
    SHORT_SIDE_PANEL = auto()


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

DIMENSION_DATA = DimensionData((BOX_X, BOX_Y, BOX_Z), mat_thickness=PLY_THICKNESS)
