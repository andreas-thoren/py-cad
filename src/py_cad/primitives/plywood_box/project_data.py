from enum import auto

from py_cad import StrAutoEnum


class Part(StrAutoEnum):
    BOTTOM = auto()
    LONG_SIDE = auto()
    LONG_SIDE_INVERSE = auto()
    SHORT_SIDE = auto()
    SHORT_SIDE_INVERSE = auto()
    TOP = auto()


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
    # Top reuses BOTTOM geometry — for this style the panels are visually identical.
    Part.TOP: PartType.BOTTOM,
}
