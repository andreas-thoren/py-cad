from dataclasses import dataclass
from enum import Enum


@dataclass
class DimensionData:
    width: int | float
    depth: int | float
    height: int | float
    material_thickness: int | float | dict[Enum, int | float]


class DimensionDataMixin:

    def __init__(
        self,
        width: int | float,
        depth: int | float,
        height: int | float,
        material_thickness: int | float | dict[str, int | float],
    ):
        """Initialize base dimensions."""
        self._x_length = width
        self._y_length = depth
        self._z_length = height
        self._material_thickness = material_thickness

    @property
    def x_length(self):
        return self._x_length

    @property
    def width(self):
        return self._x_length

    @property
    def y_length(self):
        return self._y_length

    @property
    def depth(self):
        return self._y_length

    @property
    def z_length(self):
        return self._z_length

    @property
    def height(self):
        return self._z_length

    @property
    def material_thickness(self):
        if isinstance(self._material_thickness, dict):
            return self._material_thickness.copy()
        return self._material_thickness

    def get_part_thickness(self, part_type: Enum) -> int | float:
        """Get the thickness of a specific part."""
        if isinstance(self._material_thickness, dict):
            try:
                return self._material_thickness[part_type]
            except KeyError as exc:
                raise ValueError(
                    f"Material thickness for {part_type} not found in mapping:"
                    f"\n{self._material_thickness}"
                ) from exc
        return self._material_thickness

