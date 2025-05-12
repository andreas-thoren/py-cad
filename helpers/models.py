"""
Base classes and utilities for part and assembly modeling using CadQuery.

Design note:
All part and metadata keys are internally normalized to lowercase strings.
This allows both str and StrEnum values to be used interchangeably in external APIs.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import StrEnum
import cadquery as cq


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


class ResolveMixin:
    """Ger metoder för att normalisera strängar och dict-nycklar/värden."""

    @staticmethod
    def normalize(item: str | StrEnum) -> str:
        return item.strip().lower()

    @classmethod
    def normalize_all(cls, items: Iterable[str | StrEnum]) -> set[str]:
        # TODO add logic for raising errors when collisions both before and after normalization
        return {cls.normalize(i) for i in items}

    @classmethod
    def normalize_map(
        cls, mapping: dict[str | StrEnum, str | StrEnum]
    ) -> dict[str, str]:
        return {cls.normalize(k): cls.normalize(v) for k, v in mapping.items()}

    @classmethod
    def _resolve_items(
        cls, initial_attr_name: str, new_attr_name: str, resolved_attr_name: str
    ) -> frozenset[str]:
        items = cls.__dict__.get(initial_attr_name)
        if items:
            return frozenset(cls.normalize_all(items))

        # # TODO Fix so that it works for multiple inheritance
        parent_items = None
        for base in cls.__mro__[1:]:
            if hasattr(base, resolved_attr_name):
                parent_items = getattr(base, resolved_attr_name)
                break
        if parent_items is None:
            raise ValueError(
                "If not subclassing concrete Builder classes must define 'part_types'."
            )

        new_items = cls.__dict__.get(new_attr_name)
        new_items = cls.normalize_all(new_items) if new_items is not None else set()
        return frozenset(parent_items | new_items)


class BuilderABC(DimensionDataMixin, ResolveMixin, ABC):
    """
    Abstract base class for all Builder classes.

    Subclasses must:
        1. Define part_types (Iterable[str] | type[StrEnum]).
           new_part_types can be defined instead of part_types if subclassing concrete
           Builder classes and you want to keep part_types defined in parents.
        2. Implement build methods for each part type.
        3. Register each build method using @BuilderABC.register(part_type).

    Custom __init__ methods (optional, for calculated dimensions etc) must:
        1. Accept dimension_data (DimensionData) as its first argument.
        2. Start by calling super().__init__(dimension_data) before custom logic.
    """

    # attributes in _setup_attributes are only used during __init_subclass__. Deleted.
    _setup_attributes = ("part_types", "new_part_types")
    part_types: Iterable[str] | type[StrEnum]
    new_part_types: Iterable[str] | type[StrEnum]

    # Resolved attributes. Dynamically assigned in __init_subclass__
    _resolved_part_types: frozenset[str]
    _builder_map: dict[str, Callable]

    @property
    def resolved_part_types(self) -> frozenset[str]:
        return self._resolved_part_types

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Resolve (normalize and add parent part_types) through resolve_items
        cls._resolved_part_types = cls._resolve_items(
            "part_types", "new_part_types", "_resolved_part_types"
        )

        # TODO validate that below inheritance fetching works
        # Make a copy of concrete parents _builder_map (if concrete parent exists)
        parent_builder_map = getattr(cls, "_builder_map", None) or {}

        # Build the child_builder_map by scanning the class for methods with registered parts
        child_builder_map = {}
        for attr in cls.__dict__.values():
            if callable(attr) and hasattr(attr, "_registered_part_type"):
                part_type = cls.normalize(attr._registered_part_type)
                child_builder_map[part_type] = attr

        # Current class_builder_map is the combined map, child definitions win if collisions.
        cls._builder_map = parent_builder_map | child_builder_map

        # Safety check: ensure all part types are mapped
        missing_parts = list(cls._resolved_part_types - set(cls._builder_map.keys()))
        if missing_parts:
            raise ValueError(
                f"{cls.__name__}._builder_map missing parts: {missing_parts}"
            )

        # Delete class attributes only used for subclass setup
        for attr in cls._setup_attributes:
            if attr in cls.__dict__:
                delattr(cls, attr)

        # TODO Add descriptor so that attempted access to this attributes makes it clear
        # that they are only intended for class setup. Point to resolved_part_types!

    def __init__(self, dimension_data: DimensionData):
        self._dimension_data = dimension_data
        self._solid_cache = {}

    def build_part(
        self, part_type: StrEnum, cached_solid: bool = False
    ) -> cq.Workplane | cq.Solid:
        """
        Builds the part for the given part_type.

        Args:
            part_type: One of the parts in part_types/new_part_types or inherited part_types.
            cached_solid: If True, returns cached Solid object; else a new Workplane.

        Returns:
            cadquery.Workplane or cadquery.Solid.
        """
        key = self.normalize(part_type)

        try:
            build_func = self._builder_map[key]
        except KeyError as exc:
            raise ValueError(
                f"Invalid part type: {part_type}! (normalized to '{key}'). "
                f"Available: {list(self._builder_map.keys())}"
            ) from exc

        if cached_solid:
            if part_type not in self._solid_cache:
                self._solid_cache[part_type] = build_func(self).val()
            return self._solid_cache[part_type]

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


class AssemblerABC(DimensionDataMixin, ResolveMixin, ABC):
    """
    Abstract base class for all Assemblers.

    Subclasses must:
        1. Define BuilderClass (subclass of BuilderABC).
        2. Define parts (Iterable[str] | type[StrEnum]).
           new_parts can be defined instead of parts if subclassing concrete
           Assembler classes and you want to keep parts defined in parents.
        3. Define part_map which should be a dict mapping part: part_type (Builder).
        4. Implement method get_metadata_map which should returns
           metadata for each part specified in parts.

    Shortcut:
        If parts is identical to BuilderClass.part_types,
        part_map should be omitted and will default to identity mapping.
    """

    # attributes in _setup_attributes are only used during __init_subclass__. Deleted.
    _setup_attributes = ("parts", "new_parts", "part_map", "BuilderClass")
    parts: Iterable[str] | type[StrEnum]
    new_parts: Iterable[str] | type[StrEnum]
    part_map: dict[str | StrEnum, str | StrEnum]
    BuilderClass: type[BuilderABC]

    # Resolved attributes. Dynamically assigned in __init_subclass__
    _resolved_parts: frozenset[str]
    _resolved_part_map: dict[str, str]
    _BuilderClass: type[BuilderABC]

    @property
    def resolved_parts(self) -> frozenset[str]:
        return self._resolved_parts

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Resolve (normalize and add parent parts) through resolve_items
        cls._resolved_parts = cls._resolve_items(
            "parts", "new_parts", "_resolved_parts"
        )

        # Check that BuilderClass is correct, move to private attribute.
        if not hasattr(cls, "BuilderClass") or not issubclass(
            cls.BuilderClass, BuilderABC
        ):
            raise TypeError(
                f"{cls.__name__} must define BuilderClass as a BuilderABC subclass."
            )
        cls._BuilderClass = cls.BuilderClass

        # Identity map shortcut for _resolved_part_map
        if cls._resolved_parts == cls._BuilderClass._resolved_part_types:
            if hasattr(cls, "part_map"):
                raise ValueError(
                    f"{cls.__name__}: should not define part_map when "
                    "parts == _BuilderClass.part_types"
                )
            cls._resolved_part_map = {part: part for part in cls._resolved_parts}
        else:  # Validate part_map
            if not hasattr(cls, "part_map") or not isinstance(cls.part_map, dict):
                raise TypeError(f"{cls.__name__} must define part_map as a dict.")

            # Validate keys of cls.part_map
            cls._resolved_part_map = cls.normalize_map(cls.part_map)
            actual_keys = frozenset(cls._resolved_part_map.keys())
            expected_keys = cls._resolved_parts
            if actual_keys != expected_keys:
                raise ValueError(
                    f"{cls.__name__}: incomplete part_map keys: "
                    f"expected {expected_keys}, got {actual_keys}"
                )

            # Validate values of cls.part_map
            actual_values = frozenset(cls._resolved_part_map.values())
            allowed_values = cls._BuilderClass._resolved_part_types
            invalid_values = actual_values - allowed_values
            if invalid_values:
                raise ValueError(
                    f"{cls.__name__}: part_map contains invalid part type values: {invalid_values}"
                )

        # Delete class attributes only used for subclass setup
        for attr in cls._setup_attributes:
            if attr in cls.__dict__:
                delattr(cls, attr)

        # TODO Add descriptor so that attempted access to this attributes makes it clear
        # that they are only intended for class setup. Point to resolved_part_types!

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
    def get_metadata_map(self) -> dict[str | StrEnum, dict]:
        """Return metadata for each part in parts"""

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
            part_type = self._resolved_part_map[part]
            solid = self.builder.build_part(part_type, cached_solid=True)
            data.append((solid, metadata))
        return data

    # TODO allow for assembly_data being passed in as var. If so do not require get_metadata_map.
    def assemble(self, assembly_parts: Iterable[StrEnum] | None = None) -> cq.Assembly:
        """
        Build an assembly from specified parts.

        Args:
            assembly_parts: Iterable of parts used in assembly. Defaults to all parts.

        Returns:
            cadquery.Assembly
        """
        assembly_parts = (
            self.normalize_all(assembly_parts)
            if assembly_parts
            else self._resolved_parts
        )
        assembly = cq.Assembly()

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
