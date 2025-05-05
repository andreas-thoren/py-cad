from abc import ABC, abstractmethod
from collections.abc import Iterable
from enum import Enum
import cadquery as cq


class DimensionMixin:

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
    def width(self):
        return self._x_length

    @property
    def depth(self):
        return self._y_length

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


class BuilderABC(DimensionMixin, ABC):
    @abstractmethod
    def build_part(self, part_type: Enum) -> cq.Workplane:
        """Build a part based on the given part type."""


class AssemblerABC(DimensionMixin, ABC):
    """
    To be used as a base class for all assemblers.
    Subclasses must implement the following:

    1. Define the following class attributes:
    - PartTypeEnum: An Enum class containing all part types.
    - BuilderClass: A concrete Builder class that inherits from BuilderABC.

    2. If additional instance variables are needed, implement a custom __init__ method.
       The custom __init__ must call super().__init__() with width, depth, height
       and material_thickness.

    3. Implement the metadata_map property.
       It must return a dictionary mapping part types (PartTypeEnum members)
       to metadata dictionaries containing kwargs for the cq.Assembly.add method.
    """

    PartTypeEnum: type[Enum]
    BuilderClass: type[BuilderABC]

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
        self._builder = self.BuilderClass()

    @property
    @abstractmethod
    def metadata_map(self) -> dict[Enum, dict]:
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
            assembly_parts (Iterable[PartTypeEnum]): Iterable of part types
                to include in the assembly.

        Returns:
            list[tuple[cq.Workplane, dict]]: List of tuples containing
                the part metadata.
        """
        assembly_data = []
        metadata_map = self.metadata_map
        for part in assembly_parts:
            try:
                metadata = metadata_map[part]
            except KeyError as exc:
                raise ValueError(f"Invalid part type: {part}") from exc

            cq_workplane = self.builder.build_part(part)
            assembly_data.append((cq_workplane, metadata))
        return assembly_data

    def assemble(self, assembly_parts: Iterable[Enum] | None = None) -> cq.Assembly:
        assembly_parts = assembly_parts or tuple(self.PartTypeEnum)
        assembly = cq.Assembly()
        for part, metadata in self._get_assembly_data(assembly_parts):
            assembly.add(part, **metadata)
        return assembly
