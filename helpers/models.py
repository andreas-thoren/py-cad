from dataclasses import dataclass
from enum import Enum


@dataclass
class DimensionData:
    width: int | float
    depth: int | float
    height: int | float
    material_thickness: int | float | dict[Enum, int | float]


class DimensionDataMixin:

    @property
    def x_length(self):
        return self._dimension_data.width

    @property
    def width(self):
        return self._dimension_data.width

    @property
    def y_length(self):
        return self._dimension_data.depth

    @property
    def depth(self):
        return self._dimension_data.depth

    @property
    def z_length(self):
        return self._dimension_data.height

    @property
    def height(self):
        return self._dimension_data.height

    @property
    def material_thickness(self):
        material_thickness = self._dimension_data.material_thickness
        if isinstance(material_thickness, dict):
            return material_thickness.copy()
        return material_thickness

    def get_part_thickness(self, part_type: Enum) -> int | float:
        """Get the thickness of a specific part."""
        material_thickness = self._dimension_data.material_thickness
        if isinstance(material_thickness, dict):
            try:
                return material_thickness[part_type]
            except KeyError as exc:
                raise ValueError(
                    f"Material thickness for {part_type} not found in mapping:"
                    f"\n{material_thickness}"
                ) from exc
        return material_thickness
