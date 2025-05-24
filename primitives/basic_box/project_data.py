from dataclasses import dataclass
from enum import StrEnum
from helpers.models import DimensionData


class Part(StrEnum):
    BOTTOM = "bottom"
    LONG_SIDE = "long side"
    LONG_SIDE_INVERSE = "long side inverse"
    SHORT_SIDE = "short side"
    SHORT_SIDE_INVERSE = "short side inverse"
    TOP = "top"


class PartType(StrEnum):
    BOTTOM = "bottom"
    LONG_SIDE_PANEL = "long side panel"
    SHORT_SIDE_PANEL = "short side panel"
    TOP = "top"


PART_TYPE_MAP = {
    Part.BOTTOM: PartType.BOTTOM,
    Part.LONG_SIDE: PartType.LONG_SIDE_PANEL,
    Part.LONG_SIDE_INVERSE: PartType.LONG_SIDE_PANEL,
    Part.SHORT_SIDE: PartType.SHORT_SIDE_PANEL,
    Part.SHORT_SIDE_INVERSE: PartType.SHORT_SIDE_PANEL,
    Part.TOP: PartType.TOP,
}


BoxDimensionData = DimensionData
