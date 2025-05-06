from abc import ABC, abstractmethod
from collections.abc import Iterable
from enum import Enum
import cadquery as cq
from .models import DimensionData, DimensionDataMixin


class BuilderABC(DimensionDataMixin, ABC):
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
        width: int | float,
        depth: int | float,
        height: int | float,
        material_thickness: int | float | dict[str, int | float],
    ):
        """
        Initialize base assembler dimensions and builder.

        Args:
            width (int | float): Total width of the assembly.
            depth (int | float): Total depth of the assembly.
            height (int | float): Total height of the assembly.
            material_thickness (int | float | dict[str, int | float]):
                Thickness of the material used, or a mapping of material names
                to thicknesses.
        """
        super().__init__(width, depth, height, material_thickness)
        self._builder = self._BuilderClass()

    @abstractmethod
    def get_metadata_map(self) -> dict[Enum, dict]:
        pass

    @property
    def builder(self) -> BuilderABC:
        return self._builder

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
