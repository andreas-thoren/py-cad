from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import StrEnum
import cadquery as cq
from .enum_helpers import create_str_enum, extend_str_enum


@dataclass
class DimensionData:
    """Can be subclassed for projects that need more dimension variables."""

    x_length: int | float
    y_length: int | float
    z_length: int | float
    material_thickness: int | float | dict[StrEnum, int | float]


class DimensionDataMixin:
    """Allows attribute access from subclasses directly to the DimensionData attributes."""

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

    def get_part_thickness(self, part_type: StrEnum) -> int | float:
        """Get the thickness of a specific part."""
        material_thickness = self._dimension_data.material_thickness
        if isinstance(material_thickness, dict):
            try:
                return material_thickness[part_type]
            except KeyError as exc:
                raise ValueError(
                    f"Material thickness for {part_type} not found in mapping:\n"
                    f"{material_thickness}"
                ) from exc
        return material_thickness

    def __getattr__(self, name):
        """Delegate missing attributes to self._dimension_data."""
        try:
            return getattr(self._dimension_data, name)
        except AttributeError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            ) from None


class NormalizationMixin:

    @staticmethod
    def normalize_item(item: str | StrEnum) -> str:
        return item.strip().lower()

    @staticmethod
    def normalize_items(items: Iterable[str] | type[StrEnum]) -> set[str]:
        # TODO add logic for raising errors when collisions both before and after normalization
        return {NormalizationMixin.normalize_item(item) for item in items}


class BuilderABC(DimensionDataMixin, NormalizationMixin, ABC):
    """
    Abstract base class for all Builder classes.

    Subclasses must:
        1. Define cls._PartTypeEnum (a StrEnum).
        2. Implement build methods for each part type.
        3. Register each build method using @BuilderABC.register(part_type).

    Custom __init__ methods (optional, for calculated dimensions etc) must:
        1. Accept dimension_data (DimensionData) as its first argument.
        2. Start by calling super().__init__(dimension_data) before custom logic.
    """

    part_types: Iterable[str] | type[StrEnum]
    new_part_types: Iterable[str] | type[StrEnum]
    _resolved_part_types: frozenset[str]
    _builder_map: dict[str, Callable]

    @property
    def resolved_part_types(self) -> frozenset[str]:
        return self._resolved_part_types

    @classmethod
    def _resolve_part_types(cls) -> frozenset[str]:
        items = cls.__dict__.get("part_types")

        if items:
            return frozenset(cls.normalize_items(items))

        # # TODO Validate that this works as expected
        parent_items: set[str] = getattr(super(cls, cls), "_resolved_part_types", None)
        if parent_items is None:
            raise ValueError(
                "If not subclassing concrete Builder classes must define 'part_types'."
            )

        new_items = cls.__dict__.get("new_part_types")
        new_items = cls.normalize_items(new_items) if new_items is not None else set()
        return frozenset(parent_items | new_items)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._resolved_part_types = cls._resolve_part_types()

        # 1. Make a copy of concrete parents _builder_map (if concrete parent exists)
        # TODO validate that below inheritance fetching works
        parent_builder_map = getattr(cls, "_builder_map", None) or {}

        # 2. Build the child_builder_map by scanning the class for methods with registered parts
        child_builder_map = {}
        for attr in cls.__dict__.values():
            if callable(attr) and hasattr(attr, "_registered_part_type"):
                part_type = cls.normalize_item(attr._registered_part_type)
                child_builder_map[part_type] = attr

        # Current class_builder_map is the combined map, child definitions win if collisions.
        cls._builder_map = parent_builder_map | child_builder_map

        # 3. Safety check: ensure all part types are mapped
        missing_parts = list(cls._resolved_part_types - set(cls._builder_map.keys()))
        if missing_parts:
            raise ValueError(
                f"{cls.__name__}._builder_map missing parts: {missing_parts}"
            )

        # 4. Delete class attributes only used for subclass setup
        delattr(cls, "part_types")
        delattr(cls, "new_part_types")

        # 5. TODO Add descriptor so that attempted access to this attributes makes it clear
        # that they are only intended for class setup. Point to resolved_part_types!

    def __init__(self, dimension_data: DimensionData):
        self._dimension_data = dimension_data
        self._solid_cache = {}

    def build_part(
        self, part_type: StrEnum, cached_solid: bool = False
    ) -> cq.Workplane | cq.Solid:
        """
        Builds the part for the given PartTypeEnum member.

        Args:
            part_type: PartTypeEnum member.
            cached_solid: If True, returns cached Solid object; else a new Workplane.

        Returns:
            cadquery.Workplane or cadquery.Solid.
        """
        try:
            build_func = self._builder_map[part_type]
        except KeyError as exc:
            raise ValueError(
                f"Invalid part type: {part_type}. Available: {list(self._builder_map.keys())}"
            ) from exc

        if cached_solid:
            func_name = build_func.__name__
            if func_name not in self._solid_cache:
                self._solid_cache[func_name] = build_func(self).val()
            return self._solid_cache[func_name]

        return build_func(self)

    def clear_cache(self) -> None:
        """Clear the solid cache."""
        self._solid_cache.clear()

    @classmethod
    def get_part(
        cls, dimension_data: DimensionData, part_type: StrEnum, *args, **kwargs
    ) -> cq.Workplane:
        """Convenience method to build a part without manually instantiating the builder."""
        builder = cls(dimension_data, *args, **kwargs)
        return builder.build_part(part_type)

    @staticmethod
    def register(part_type: StrEnum) -> Callable:
        """Decorator to register build methods."""

        def decorator(func):
            # Defer attaching into _builder_map until __init_subclass__
            func._registered_part_type = part_type
            return func

        return decorator


class AssemblerABC(DimensionDataMixin, NormalizationMixin, ABC):
    """
    Abstract base class for all Assemblers.

    Subclasses must:
        1. Define cls._BuilderClass (subclass of BuilderABC).
        2. Define cls._PartEnum (a StrEnum of assembly parts).
        3. Define cls._part_type_map (maps PartEnum -> PartTypeEnum).
        4. Implement method get_metadata_map which should returns
           metadata for each PartEnum member.

    Shortcut:
        If _PartEnum is identical to _BuilderClass._PartTypeEnum,
        _part_type_map should be omitted and will default to identity mapping.
    """

    _BuilderClass: type[BuilderABC]
    _PartEnum: type[StrEnum]
    _part_type_map: dict[StrEnum, StrEnum]

    @property
    def PartEnum(self) -> type[StrEnum]:  # pylint: disable=invalid-name
        return self._PartEnum

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "_BuilderClass") or not issubclass(
            cls._BuilderClass, BuilderABC
        ):
            raise TypeError(
                f"{cls.__name__} must define _BuilderClass as a BuilderABC subclass."
            )
        if not hasattr(cls, "_PartEnum") or not issubclass(cls._PartEnum, StrEnum):
            raise TypeError(
                f"{cls.__name__} must define _PartEnum as an StrEnum subclass."
            )

        # Identity map shortcut
        if cls._PartEnum is cls._BuilderClass._PartTypeEnum:
            if hasattr(cls, "_part_type_map"):
                raise ValueError(
                    f"{cls.__name__}: should not define _part_type_map when "
                    "_PartEnum == _BuilderClass._PartTypeEnum."
                )
            cls._part_type_map = {member: member for member in cls._PartEnum}
            return

        # TODO move all validation regarding _part_type_map to its own method
        # TODO postpone validation until first call of assemble. Store _is_valid instance attribute.
        # Validate _part_type_map
        if not hasattr(cls, "_part_type_map") or not isinstance(
            cls._part_type_map, dict
        ):
            raise TypeError(f"{cls.__name__} must define _part_type_map as a dict.")

        # Validate keys of cls._part_type_map
        actual_keys = set(cls._part_type_map.keys())
        expected_keys = set(cls._PartEnum)
        if actual_keys != expected_keys:
            raise ValueError(
                f"{cls.__name__}: incomplete _part_type_map keys: "
                f"expected {expected_keys}, got {actual_keys}"
            )

        # Validate values of cls._part_type_map
        actual_values = set(cls._part_type_map.values())
        allowed_values = set(cls._BuilderClass._PartTypeEnum)
        invalid_values = actual_values - allowed_values
        if invalid_values:
            raise ValueError(
                f"{cls.__name__}: _part_type_map contains invalid PartType values: {invalid_values}"
            )

    def __init__(self, dimension_data: DimensionData):
        """
        Initialize assembler and builder.

        Args:
            dimension_data (DimensionData): DimensionData instance containing
                the dimensions of the assembly.
        """
        self._dimension_data = dimension_data
        self.builder = self._BuilderClass(dimension_data)

    @abstractmethod
    def get_metadata_map(self) -> dict[StrEnum, dict]:
        """Return metadata for each PartEnum member."""

    def _get_assembly_data(
        self, assembly_parts: Iterable[StrEnum]
    ) -> list[tuple[cq.Workplane, dict]]:
        """Helper used by 'assemble' to build parts and attach metadata."""
        data = []
        metadata_map = self.get_metadata_map()
        for part in assembly_parts:
            if part not in metadata_map:
                raise ValueError(f"Missing metadata for part: {part}")

            metadata = metadata_map[part]
            part_type = self._part_type_map[part]
            solid = self.builder.build_part(part_type, cached_solid=True)
            data.append((solid, metadata))
        return data

    # TODO allow for assembly_data being passed in as var. If so do not require get_metadata_map.
    def assemble(self, assembly_parts: Iterable[StrEnum] | None = None) -> cq.Assembly:
        """
        Build an assembly from specified parts.

        Args:
            assembly_parts: Iterable of PartEnum members. Defaults to all parts.

        Returns:
            cadquery.Assembly
        """
        assembly_parts = assembly_parts or tuple(self.PartEnum)
        assembly = cq.Assembly()
        # TODO if assembly_data is not being passed in check _build_part_map
        for solid, metadata in self._get_assembly_data(assembly_parts):
            assembly.add(solid, **metadata)
        return assembly

    @classmethod
    def get_assembly(
        cls,
        dimension_data: DimensionData,
        *args,
        assembly_parts: Iterable[StrEnum] | None = None,
        **kwargs,
    ) -> cq.Assembly:
        """Convenience method to create an assembly directly."""
        assembler = cls(dimension_data, *args, **kwargs)
        return assembler.assemble(assembly_parts)
