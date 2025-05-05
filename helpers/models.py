from dataclasses import dataclass
from enum import Enum


@dataclass
class DimensionData:
    width: int | float
    depth: int | float
    height: int | float
    material_thickness: int | float | dict[Enum, int | float]
