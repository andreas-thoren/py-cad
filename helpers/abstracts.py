from abc import ABC, abstractmethod
from collections.abc import Iterable
from enum import Enum
import cadquery as cq

class BuilderABC(ABC):
    @abstractmethod
    def build_part(self, part_type: Enum) -> cq.Workplane:
        """Build a part based on the given part type."""

class AssemblerABC(ABC):
    PartTypeEnum: type[Enum]

    @abstractmethod
    def __init__(
        self,
        width: int | float,
        depth: int | float,
        height: int | float,
        material_thickness: int | float,
    ):
        pass

    @property
    @abstractmethod
    def _x_length(self):
        pass

    @property
    @abstractmethod
    def _y_length(self):
        pass

    @property
    @abstractmethod
    def _z_length(self):
        pass

    @property
    @abstractmethod
    def _material_thickness(self):
        pass

    @property
    @abstractmethod
    def builder(self) -> BuilderABC:
        pass

    @property
    @abstractmethod
    def metadata_map(self) -> dict[type[Enum], dict]:
        pass

    @property
    def width(self):
        return self._x_length

    @property
    def depth(self):
        return self._y_length

    @property
    def height(self):
        return self._z_length / 2

    @property
    def material_thickness(self):
        return self._material_thickness

    def get_assembly_data(
        self, assembly_parts: Iterable[type[Enum]]
    ) -> list[tuple[cq.Workplane, dict]]:

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

    def assemble(
        self, assembly_parts: Iterable[type[Enum]] | None = None
    ) -> cq.Assembly:
        assembly_parts = assembly_parts or tuple(self.PartTypeEnum)
        assembly = cq.Assembly()
        for part, metadata in self.get_assembly_data(assembly_parts):
            assembly.add(part, **metadata)
        return assembly
