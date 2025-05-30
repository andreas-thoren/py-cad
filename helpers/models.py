"""
Base classes and utilities for part and assembly modeling using CadQuery.
"""

from abc import ABC, abstractmethod
from collections import UserDict
from collections.abc import Callable, Iterable, Sequence
from enum import StrEnum
from typing import Any, Generic, TypeVar
import cadquery as cq

K = TypeVar("K")
V = TypeVar("V")


class NormalizedDict(UserDict, Generic[K, V]):
    """
    Used for all dicts where part types are used as keys.
    Normalizes keys to lowercase stripped strings (both for setting/getting items).
    """

    @staticmethod
    def normalize_item(key: K, raise_error: bool = False) -> str | Any:
        """
        Normalize keys to lowercase strings. If raise_error is False will return
        the original key withouth raising if original key is not a string.
        """
        try:
            return key.strip().lower()
        except AttributeError as exc:
            if raise_error:
                raise TypeError(
                    f"Keys must be strings, got {type(key).__name__}: {key!r}"
                ) from exc
            return key

    def __getitem__(self, key: K) -> V:
        return super().__getitem__(self.normalize_item(key))

    def __setitem__(self, key: K, value: V) -> None:
        super().__setitem__(self.normalize_item(key, raise_error=True), value)

    def __delitem__(self, key: K) -> None:
        super().__delitem__(self.normalize_item(key))

    def __contains__(self, key: K) -> bool:
        return super().__contains__(self.normalize_item(key))


class ResolveMixin:
    """Provides methods for normalizing strings and dictionary keys/values."""

    @staticmethod
    def normalize(item: str) -> str:
        return NormalizedDict.normalize_item(item, raise_error=True)

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
    def normalize_values(cls, mapping: dict[str, Any]) -> dict[str, Any]:
        return {k: cls.normalize(v) for k, v in mapping.items()}

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


class BasicDimensionData:
    x_len: int | float
    y_len: int | float
    z_len: int | float
    _has_basic_dimensions: bool

    def __init__(
        self,
        basic_dimensions: tuple[int | float, int | float, int | float] | None = None,
        freeze_existing_attributes: bool = False,
        **extra_dimensions: Any,
    ):
        """
        Basic dimension data class with X, Y, Z dimensions and optional extra dimensions.
        Basic dimensions can be provided after __init__ with add_basic_dimensions.
        This allows for flexible initialization and subclassing.
        """

        if basic_dimensions is not None:
            self.set_basic_dimensions(basic_dimensions, **extra_dimensions)
        else:
            self._has_basic_dimensions = False
            self.update(**extra_dimensions)

        if freeze_existing_attributes:
            self.freeze_existing_attributes()

    def update(self, **extra_dimensions: Any):
        """
        Update dimensions with new values.
        Raises AttributeError if _freeze_existing_attributes is True and dimension already exists.
        """
        for dimension, value in extra_dimensions.items():
            setattr(self, dimension, value)

    def set_basic_dimensions(
        self,
        basic_dimensions: tuple[int | float, int | float, int | float],
        **extra_dimensions: Any,
    ) -> None:
        """Add basic dimensions to the instance. Optionally accepts extra dimensions."""
        if not isinstance(basic_dimensions, Sequence) or len(basic_dimensions) != 3:
            raise TypeError(
                "basic_dimensions must be a Sequence (tuple, list, ...) of three numbers (x_len, y_len, z_len)."
            )
        self.update(**extra_dimensions)
        x_len, y_len, z_len = basic_dimensions
        # Basic dimensions come last to take priority over extra dimensions.
        self.update(x_len=x_len, y_len=y_len, z_len=z_len)
        self._has_basic_dimensions = True

    def freeze_existing_attributes(self):
        """Freeze existing attributes to prevent modification."""
        if not self._has_basic_dimensions:
            raise ValueError(
                "Cannot freeze existing attributes before setting basic dimensions."
            )
        self._freeze_existing_attributes = True

    def __setattr__(self, name, value):
        # Allow setting anything if not frozen or if setting _freeze_existing_attributes itself
        if (
            getattr(self, "_freeze_existing_attributes", False)
            and name != "_freeze_existing_attributes"
        ):
            if name in self.__dict__:
                raise AttributeError(
                    f"Attributes of {self.__class__.__name__} instances "
                    "are immutable after freeze_existing_attributes() has been called."
                )
        super().__setattr__(name, value)

    def __repr__(self):
        attrs = []
        for attr, value in self.__dict__.items():
            if attr.startswith("_") or callable(value):
                continue
            attrs.append(f"{attr}={value!r}")
        attrs.sort()  # Sort attributes for consistent output
        return f"{self.__class__.__name__}({', '.join(attrs)})"


class DimensionData(BasicDimensionData, ResolveMixin):
    """Can be subclassed for projects that need more dimension variables."""

    def __init__(
        self,
        basic_dimensions: tuple[int | float, int | float, int | float],
        part_type_attributes: dict[str, Any] | None = None,
        **extra_dimensions: Any,
    ):
        """
        Initialize DimensionData with dimensions and material thickness.

        Args:
            basic_dimensions (tuple): Tuple of (x_len, y_len, z_len).
            part_type_attributes (dict): Optional attributes mapped from part types.
              Should be a dictionary where keys are then name of the attribute to be created.
              Values should be a, nested, dictionary with part types as keys
              and their corresponding values as dict values.
            extra_dimensions: Additional dimensions as keyword arguments.
        """
        # Call super init first to set project basic dimensions.
        super().__init__(basic_dimensions=basic_dimensions, **extra_dimensions)

        # Initialize _part_types_dimensions as a NormalizedDict
        self._part_types_dimensions = NormalizedDict()

        # If part_type_attributes is provided:
        # - Create a BasicDimensionData instance and add it to _part_types_dimensions.
        # - Add the attributes to the instances.
        for attr, dict_val in (part_type_attributes or {}).items():
            if not isinstance(dict_val, dict):
                raise TypeError(
                    f"Part type attributes for '{attr}' must be a dictionary mapping part types to values."
                )

            for part_type, val in dict_val.items():
                basic_dim_data = self._part_types_dimensions.setdefault(
                    part_type, BasicDimensionData()
                )
                setattr(basic_dim_data, attr, val)

        # Call get_part_types_dimensions -> convert to a NormalizedDict instance
        # A
        new_part_types_dimensions = NormalizedDict(**self.get_part_types_dimensions())
        for part_type, dimensions in new_part_types_dimensions.items():
            basic_dim_data: BasicDimensionData = self._part_types_dimensions.setdefault(
                part_type, BasicDimensionData()
            )
            basic_dims, extra_dims = self._normalize_part_type_dimensions(dimensions)
            basic_dim_data.set_basic_dimensions(basic_dims, **extra_dims)
            basic_dim_data.freeze_existing_attributes()
        self.freeze_existing_attributes()  # basic dimensions are set at super().__init__.

    @property
    def part_types_dimensions(self) -> NormalizedDict[str, BasicDimensionData]:
        """Get the resolved part types dimensions."""
        return self._part_types_dimensions.copy()

    def get_part_types_dimensions(
        self,
    ) -> dict[
        StrEnum | str,
        tuple[int | float, int | float, int | float]
        | tuple[tuple[int | float, int | float, int | float], dict[str, Any]],
    ]:
        """
        Meant to be overriden by subclasses that needs dimensions for specific part types.
        If overriden must return a mapping of part types to dimension tuples or (tuple, dict) pairs.
        """
        return {}

    @staticmethod
    def _normalize_part_type_dimensions(
        dimensions: (
            tuple[int | float, int | float, int | float]
            | tuple[tuple[int | float, int | float, int | float], dict[str, Any]]
        ),
    ) -> tuple[tuple[int | float, int | float, int | float], dict[str, Any]]:
        match dimensions:
            case (x, y, z):
                extras = {}
            case ((x, y, z), {**extras}):
                pass
            case _:
                raise TypeError(
                    "get_part_types_dimensions must return either a tuple of three "
                    "numbers (x_len, y_len, z_len) or a tuple containing a tuple of three "
                    "numbers and a dictionary of extra dimensions. "
                )
        return (x, y, z), extras

    def __getitem__(self, part_type) -> BasicDimensionData:
        try:
            return self._part_types_dimensions[part_type]
        except KeyError as exc:
            raise KeyError(
                f"Part type '{part_type}' not found. Implement get_part_types_dimensions "
                f"on {self.__class__.__name__} to provide dimensions for specific part types."
            ) from exc


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

    # Resolved attributes. Dynamically assigned in __init_subclass__
    _resolved_part_types: frozenset[str]
    _builder_map: NormalizedDict[str, Callable]

    @property
    def part_types(self) -> frozenset[str]:
        return self._resolved_part_types

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Make a copy of concrete parents _builder_map (if concrete parent exists)
        parent_builder_map = cls.get_parent_items("_builder_map") or NormalizedDict()

        # Build the child_builder_map by scanning the class for methods with registered parts
        child_builder_map = NormalizedDict()
        for attr in cls.__dict__.values():
            if callable(attr) and hasattr(attr, "_registered_part_type"):
                part_type = attr._registered_part_type
                child_builder_map[part_type] = attr

        # Current class_builder_map is the combined map, child definitions win if collisions.
        cls._builder_map = parent_builder_map | child_builder_map

        # Resolve part_types from the builder map
        cls._resolved_part_types = frozenset(cls._builder_map.keys())

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
            func._registered_part_type = part_type  # pylint: disable=protected-access
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
        "part_map",
        "BuilderClass",
    )
    # part_map: dict[str, str], optional, maps part names to part types.
    BuilderClass: type[BuilderABC]

    # Resolved attributes. Dynamically assigned in __init_subclass__
    _resolved_part_map: dict[str, str]
    _BuilderClass: type[BuilderABC]
    # _explicit_part_map: dict[str, str], will be set if part_map is defined.

    @property
    def resolved_part_map(self) -> dict[str, str]:
        return self._resolved_part_map.copy()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Check that BuilderClass is correct, move to private attribute.
        if not hasattr(cls, "BuilderClass") or not issubclass(
            cls.BuilderClass, BuilderABC
        ):
            raise TypeError(
                f"{cls.__name__} must define BuilderClass as a BuilderABC subclass."
            )
        cls._BuilderClass = cls.BuilderClass

        # Validate and normalize part_map
        part_map = cls.__dict__.get("part_map", {})
        if not isinstance(part_map, dict):
            raise TypeError(f"{cls.__name__} part_map must be a dict.")
        part_map = NormalizedDict(cls.normalize_values(part_map))

        cls._resolved_part_map = cls._resolve_part_map(part_map)
        cls._validate_resolved_part_map()

        # Save private _explicit_part_map attr if part_map was defined.
        # Must come after _resolved_part_map is set since hasattr checks for it.
        if part_map:
            cls._explicit_part_map = part_map

        # Delete class attributes only used for subclass setup
        for attr in cls._setup_attributes:
            if attr in cls.__dict__:
                delattr(cls, attr)

        # TODO Add descriptor so that attempted access to this attributes makes it clear
        # that they are only intended for class setup. Point to resolved_part_types!

    @classmethod
    def _resolve_part_map(
        cls, part_map: NormalizedDict[str, str]
    ) -> NormalizedDict[str, str]:
        """
        Resolve and returns part_map. 3 potential cases:
        1. If part_map is defined in any concrete subclass, resolved_part_map
            is union of inherited and current part_map. Current part_map has precedence if collisions.
        2. If part_map is defined in the current class only, use it directly.
        3. If no part_map is defined in any class in MRO, use identity mapping for all parts.
        """
        if hasattr(cls, "_explicit_part_map"):
            parent_part_map = (
                cls.get_parent_items("_resolved_part_map") or NormalizedDict()
            )
            return parent_part_map | part_map

        if part_map:
            return part_map

        part_types = cls._BuilderClass._resolved_part_types  # pylint: disable=w0212
        return NormalizedDict({part: part for part in part_types})

    @classmethod
    def _validate_resolved_part_map(cls):
        # Validate values of cls.part_map
        actual_values = frozenset(cls._resolved_part_map.values())
        allowed_values = cls._BuilderClass._resolved_part_types  # pylint: disable=w0212
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
            else self._resolved_part_map.keys()
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
