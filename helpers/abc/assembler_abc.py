from abc import ABC, abstractmethod
from enum import Enum
import cadquery as cq

class AssemblerABC(ABC):
    PartEnum: Enum

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
    def width(self):
        return self._x_length
    
    @property
    @abstractmethod
    def _y_length(self):
        pass

    @property
    def depth(self):
        return self._y_length

    @property
    @abstractmethod
    def _z_length(self):
        pass

    @property
    def height(self):
        return self._z_length / 2

    @property
    @abstractmethod
    def metadata_map(self) -> dict[PartEnum, dict]:
        pass

    def get_assembly_data(
        self, assembly_parts: Iterable[PartEnum]
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

    def assemble(self, assembly_parts: Iterable[PartEnum] | None = None) -> cq.Assembly:
        assembly_parts = assembly_parts or tuple(self.PartEnum)
        assembly = cq.Assembly()
        for part, metadata in self.get_assembly_data(assembly_parts):
            assembly.add(part, **metadata)
        return assembly
