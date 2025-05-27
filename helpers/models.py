"""
Base classes and utilities for part and assembly modeling using CadQuery.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from enum import StrEnum
from typing import Any
import cadquery as cq


class BasicDimensionData:
    def __init__(
        self,
        x_len: int | float,
        y_len: int | float,
        z_len: int | float,
        **extra_dimensions: Any,
    ):
        """Basic dimension data class with X, Y, Z dimensions and optional extra dimensions."""
        self.x_len = x_len
        self.y_len = y_len
        self.z_len = z_len
        for dimension, value in extra_dimensions.items():
            setattr(self, dimension, value)

        self._frozen = True

    def __setattr__(self, name, value):
        # Allow setting anything if not frozen or if setting _frozen itself
        if getattr(self, "_frozen", False) and name != "_frozen":
            raise AttributeError(
                f"{self.__class__.__name__} is frozen, cannot modify '{name}'"
            )
        super().__setattr__(name, value)


class DimensionData(BasicDimensionData):
    """Can be subclassed for projects that need more dimension variables."""

    def __init__(
        self,
        x_len: int | float,
        y_len: int | float,
        z_len: int | float,
        material_thickness: int | float | dict[str, int | float],
        **extra_dimensions: Any,
    ):
        """
        Initialize DimensionData with dimensions and material thickness.

        Args:
            x_len: Length in X direction.
            y_len: Length in Y direction.
            z_len: Length in Z direction.
            material_thickness: Thickness of the material or a mapping of part types to thicknesses.
            extra_dimensions: Additional dimensions as keyword arguments.
        """
        self._material_thickness = material_thickness
        # Super needs to come last due to _frozen attribute
        super().__init__(x_len=x_len, y_len=y_len, z_len=z_len, **extra_dimensions)

    @property
    def material_thickness(self):
        material_thickness = self._material_thickness
        if isinstance(material_thickness, dict):
            return material_thickness.copy()
        return material_thickness

    def get_part_thickness(self, part_type: str) -> int | float:
        """Get the thickness of a specific part."""
        material_thickness = self._material_thickness
        if isinstance(material_thickness, dict):
            try:
                return material_thickness[part_type]
            except KeyError as exc:
                raise ValueError(
                    f"Material thickness for {part_type} not found in mapping:\n"
                    f"{material_thickness}"
                ) from exc
        return material_thickness


class ResolveMixin:
    """Provides methods for normalizing strings and dictionary keys/values."""

    @staticmethod
    def normalize(item: str) -> str:
        return item.strip().lower()

    @classmethod
    def normalize_all(cls, items: Iterable[str] | type[StrEnum]) -> set[str]:
        # TODO add logic for raising errors when collisions both before and after normalization
        return {cls.normalize(i) for i in items}

    @classmethod
    def normalize_map(cls, mapping: dict[str, str]) -> dict[str, str]:
        return {cls.normalize(k): cls.normalize(v) for k, v in mapping.items()}

    @classmethod
    def normalize_keys(cls, mapping: dict[str, Any]) -> dict[str, Any]:
        return {cls.normalize(k): v for k, v in mapping.items()}

    @classmethod
    def normalize_items(
        cls, items: set[str] | dict[str, str]
    ) -> set[str] | dict[str, str]:
        normalize_func = (
            cls.normalize_map if isinstance(items, dict) else cls.normalize_all
        )
        return normalize_func(items)

    @classmethod
    def get_parent_items(
        cls,
        attr_name: str,
    ) -> set[str] | dict[str, str] | None:
        # Loop through ancestors creating parent_items
        parent_items = None
        for base in cls.__mro__[1:]:
            older_parent_items = getattr(base, attr_name, None)
            if older_parent_items is None:
                continue

            if parent_items is None:
                parent_items = older_parent_items
            else:
                # Younger parents come first in mro and should override older parents
                parent_items = older_parent_items | parent_items

        return parent_items

    @classmethod
    def resolve_items(
        cls,
        attr_name: str,
        resolved_attr_name: str,
        normalize: bool = True,
    ) -> set[str] | dict[str, str]:

        parent_items = cls.get_parent_items(resolved_attr_name)
        items = cls.__dict__.get(attr_name)

        if items is None:
            if parent_items is None:
                raise ValueError(
                    f"{cls.__name__} must define {attr_name} if not inheriting from a concrete class that does."
                )
            return parent_items

        items = cls.normalize_items(items) if normalize else items

        # Return the combined items datatype from parent_items and new items.
        # New items will 'win' if collisions
        return parent_items | items if parent_items is not None else items


class BuilderABC(ResolveMixin, ABC):
    """
    Abstract base class for all Builder classes.

    Subclasses must:
        1. Define part_types (Iterable[str] | type[StrEnum]).
        2. Implement build methods for each part type.
        3. Register each build method using @BuilderABC.register(part_type).

    Custom __init__ methods (optional, for calculated dimensions etc) must:
        1. Accept dim (DimensionData) as its first argument.
        2. Start by calling super().__init__(dim) before custom logic.
    """

    part_types: Iterable[str] | type[StrEnum]

    # Resolved attributes. Dynamically assigned in __init_subclass__
    _resolved_part_types: frozenset[str]
    _builder_map: dict[str, Callable]

    @property
    def resolved_part_types(self) -> frozenset[str]:
        return self._resolved_part_types

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Resolve (normalize and add parent part_types) through resolve_items
        cls._resolved_part_types = frozenset(
            cls.resolve_items("part_types", "_resolved_part_types")
        )

        # Make a copy of concrete parents _builder_map (if concrete parent exists)
        parent_builder_map = cls.get_parent_items("_builder_map") or {}

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

        # Delete "part_types" which is only used for subclass setup
        if "part_types" in cls.__dict__:
            delattr(cls, "part_types")

        # TODO Add descriptor so that attempted access to this attributes makes it clear
        # that they are only intended for class setup. Point to resolved_part_types!

    def __init__(self, dim: DimensionData):
        self._dim = dim
        self._solid_cache = {}

    @property
    def dim(self) -> DimensionData:
        """Get the DimensionData instance used by this builder."""
        return self._dim

    def build_part(
        self, part_type: str, cached_solid: bool = False
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
            if key not in self._solid_cache:
                self._solid_cache[key] = build_func(self).val()
            return self._solid_cache[key]

        return build_func(self)

    def clear_cache(self) -> None:
        """Clear the solid cache."""
        self._solid_cache.clear()

    @classmethod
    def get_part(
        cls, dim: DimensionData, part_type: str, *args, **kwargs
    ) -> cq.Workplane:
        """Convenience method to build a part without manually instantiating the builder."""
        builder = cls(dim, *args, **kwargs)
        return builder.build_part(part_type)

    @staticmethod
    def register(part_type: str) -> Callable:
        """Decorator to register build methods."""

        def decorator(func):
            # Defer attaching into _builder_map until __init_subclass__
            func._registered_part_type = part_type
            return func

        return decorator


class AssemblerABC(ResolveMixin, ABC):
    """
    Abstract base class for all Assemblers.

    Subclasses must:
        1. Define BuilderClass (subclass of BuilderABC).
        2. Define parts (Iterable[str] | type[StrEnum]).
        3. Define part_map which should be a dict mapping part: part_type (Builder).
        4. Implement method get_metadata_map which should returns
           metadata for each part specified in parts.

    Shortcut:
        If parts is identical to BuilderClass.part_types,
        part_map can be omitted and will default to identity mapping.
    """

    # attributes in _setup_attributes are only used during __init_subclass__. Deleted.
    _setup_attributes = (
        "parts",
        "part_map",
        "BuilderClass",
    )
    parts: Iterable[str] | type[StrEnum]
    part_map: dict[str, str]
    BuilderClass: type[BuilderABC]

    # Resolved attributes. Dynamically assigned in __init_subclass__
    _resolved_parts: frozenset[str]
    _resolved_part_map: dict[str, str]
    _BuilderClass: type[BuilderABC]

    @property
    def resolved_parts(self) -> frozenset[str]:
        return self._resolved_parts

    @property
    def resolved_part_map(self) -> dict[str, str]:
        return self._resolved_part_map.copy()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Resolve (normalize and add parent parts) through resolve_items
        cls._resolved_parts = frozenset(cls.resolve_items("parts", "_resolved_parts"))

        # Check that BuilderClass is correct, move to private attribute.
        if not hasattr(cls, "BuilderClass") or not issubclass(
            cls.BuilderClass, BuilderABC
        ):
            raise TypeError(
                f"{cls.__name__} must define BuilderClass as a BuilderABC subclass."
            )
        cls._BuilderClass = cls.BuilderClass

        # Validate correct part_map if not using identity map
        if hasattr(cls, "part_map"):
            if not isinstance(cls.part_map, dict):
                raise TypeError(f"{cls.__name__} part_map must be a dict.")

            cls._resolved_part_map = cls.resolve_items("part_map", "_resolved_part_map")
            cls._validate_resolved_part_map()
        elif cls._resolved_parts == cls._BuilderClass._resolved_part_types:
            # Identity map shortcut for _resolved_part_map
            cls._resolved_part_map = {part: part for part in cls._resolved_parts}
        else:
            raise TypeError(f"{cls.__name__} must define part_map as a dict.")

        # Delete class attributes only used for subclass setup
        for attr in cls._setup_attributes:
            if attr in cls.__dict__:
                delattr(cls, attr)

        # TODO Add descriptor so that attempted access to this attributes makes it clear
        # that they are only intended for class setup. Point to resolved_part_types!

    @classmethod
    def _validate_resolved_part_map(cls):
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

    def __init__(self, dim: DimensionData):
        """
        Initialize assembler and builder.

        Args:
            dim (DimensionData): DimensionData instance containing
                the dimensions of the assembly.
        """
        self._dim = dim
        self.builder = self._BuilderClass(dim)

    @property
    def dim(self) -> DimensionData:
        """Get the DimensionData instance used by this assembler."""
        return self._dim

    @abstractmethod
    def get_metadata_map(self) -> dict[str, dict]:
        """Return metadata for each part in parts"""

    def get_resolved_metadata_map(self) -> dict[str, dict[str, Any]]:
        resolved_map = self.normalize_keys(self.get_metadata_map())

        # Loop through ancester updating resolved_map
        for base in self.__class__.__mro__[1:]:
            parent_func = getattr(base, "get_metadata_map", None)
            if parent_func is None or hasattr(parent_func, "__isabstractmethod__"):
                continue

            parent_map = parent_func(self)  # pylint: disable=not-callable
            # Younger parents come first in mro and should override older parents
            resolved_map = self.normalize_keys(parent_map) | resolved_map

        return resolved_map

    def _get_assembly_data(
        self, normalized_assembly_parts: Iterable[str]
    ) -> list[tuple[cq.Workplane, dict]]:
        """Helper used by 'assemble' to build parts and attach metadata."""
        data = []
        resolved_metadata_map = self.get_resolved_metadata_map()

        for part in normalized_assembly_parts:
            if part not in resolved_metadata_map:
                raise ValueError(f"Missing metadata for part: {part}")

            metadata = resolved_metadata_map[part]
            part_type = self._resolved_part_map[part]
            solid = self.builder.build_part(part_type, cached_solid=True)
            data.append((solid, metadata))
        return data

    def assemble(self, assembly_parts: Iterable[str] | None = None) -> cq.Assembly:
        """
        Build an assembly from specified parts.

        Args:
            assembly_parts: Iterable of parts used in assembly. Defaults to all parts.

        Returns:
            cadquery.Assembly
        """
        assembly_parts: frozenset[str] = (
            frozenset(self.normalize_all(assembly_parts))
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
        dim: DimensionData,
        *args,
        assembly_parts: Iterable[str] | None = None,
        **kwargs,
    ) -> cq.Assembly:
        """Convenience method to create an assembly directly."""
        assembler = cls(dim, *args, **kwargs)
        return assembler.assemble(assembly_parts)
