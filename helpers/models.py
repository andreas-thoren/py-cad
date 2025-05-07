from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
import cadquery as cq


@dataclass
class DimensionData:
    x_length: int | float
    y_length: int | float
    z_length: int | float
    material_thickness: int | float | dict[Enum, int | float]


class DimensionDataMixin:

    @property
    def x_length(self):
        return self._dimension_data.x_length

    @property
    def y_length(self):
        return self._dimension_data.y_length

    @property
    def z_length(self):
        return self._dimension_data.z_length

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



class BuilderABC(DimensionDataMixin, ABC):
    def __init__(self, dimension_data: DimensionData):
        self._dimension_data = dimension_data

    @abstractmethod
    def build_part(self, part_type: Enum) -> cq.Workplane:
        """Build a part based on the given part type."""


class AssemblerABC(DimensionDataMixin, ABC):
    """
    To be used as a base class for all assemblers.
    Subclasses must implement the following:

    1. Define the following class attributes:
    - _PartTypeEnum: An Enum class containing all part types.
    - _BuilderClass: A concrete Builder class that inherits from BuilderABC.

    2. If additional instance variables are needed, implement a custom __init__ method.
       The custom __init__ must call super().__init__() with width, depth, height
       and material_thickness.

    3. Implement the get_metadata_map method.
       It must return a dictionary mapping part types (_PartTypeEnum members)
       to metadata dictionaries containing kwargs for the cq.Assembly.add method.
    """

    _PartTypeEnum: type[Enum]
    _BuilderClass: type[BuilderABC]

    def __init__(
        self,
        dimension_data: DimensionData,
    ):
        """
        Initialize base assembler dimensions and builder.

        Args:
            dimension_data (DimensionData): DimensionData instance containing
                the dimensions of the assembly.
        """
        self._dimension_data = dimension_data
        self.builder = self._BuilderClass(dimension_data)

    @abstractmethod
    def get_metadata_map(self) -> dict[Enum, dict]:
        pass

    def _get_assembly_data(
        self, assembly_parts: Iterable[Enum]
    ) -> list[tuple[cq.Workplane, dict]]:
        """
        Build parts and collect their metadata.

        Args:
            assembly_parts (Iterable[_PartTypeEnum]): Iterable of part types
                to include in the assembly.

        Returns:
            list[tuple[cq.Workplane, dict]]: List of tuples containing
                the part metadata.
        """
        assembly_data = []
        metadata_map = self.get_metadata_map()
        for part in assembly_parts:
            try:
                metadata = metadata_map[part]
            except KeyError as exc:
                raise ValueError(f"Invalid part type: {part}") from exc

            cq_workplane = self.builder.build_part(part)
            assembly_data.append((cq_workplane, metadata))
        return assembly_data

    def assemble(self, assembly_parts: Iterable[Enum] | None = None) -> cq.Assembly:
        assembly_parts = assembly_parts or tuple(self._PartTypeEnum)
        assembly = cq.Assembly()
        for part, metadata in self._get_assembly_data(assembly_parts):
            assembly.add(part, **metadata)
        return assembly
