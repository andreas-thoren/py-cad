from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum
import cadquery as cq


@dataclass
class DimensionData:
    """Can be subclassed for projects that need more dimension variables"""

    x_length: int | float
    y_length: int | float
    z_length: int | float
    material_thickness: int | float | dict[Enum, int | float]


class DimensionDataMixin:
    """Allows attribute access from subclasses directly to the DimensionData attributes"""

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

    def __getattr__(self, name):
        """
        Delegate attribute access to self._dimension_data if the attribute
        does not exist on self. Only called if normal attribute lookup fails.
        If the attribute is missing on _dimension_data too, raise a clean AttributeError
        that mentions the outer class (self), not _dimension_data.
        """
        try:
            return getattr(self._dimension_data, name)
        except AttributeError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            ) from None


class BuilderABC(DimensionDataMixin, ABC):
    """
    To be used as a base class for all Builder classes. Define concrete subclasses
    in the parts.py module inside each project/template folder. The parts module should also
    define a Part enum to be used both by the BuilderABC subclass and by the concrete
    AssemblerABC subclass in assembly.py.

    Builder subclasses must implement the following:
    1. If calculated part dimensions are needed, define a custom __init__ method that
       accepts dimension_data (DimensionData) as its first argument. The custom __init__
       must start by calling super().__init__(dimension_data). Defining custom logic
       below the super call allows leveraging the DimensionDataMixin to access
       dimension data for calculating part measurements.
    2. Define methods for building the different parts (project-specific).
    3. Builder subclasses must implement methods to build parts and register them
       using BuilderABC.register(Part.member1, Part.member2, ...)
    """

    _PartTypeEnum: type[Enum]  # Must be set by subclasses
    _builder_map: dict[Enum, Callable]  # Auto created in __init_subclass__

    @property
    def PartTypeEnum(self) -> type[Enum]:  # pylint: disable=invalid-name
        return self._PartTypeEnum

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "_PartTypeEnum") or not issubclass(cls._PartTypeEnum, Enum):
            raise TypeError(
                f"{cls.__name__} must define _PartTypeEnum as an Enum subclass."
            )

        # Automatically create empty part map
        cls._builder_map = {}

        # Scan the class for methods with registered parts
        for attr in cls.__dict__.values():
            if callable(attr) and hasattr(attr, "_registered_part_type"):
                part_type = attr._registered_part_type
                cls._builder_map[part_type] = attr

        # Safety check: ensure all Enum members are mapped
        missing_parts = [
            member for member in cls._PartTypeEnum if member not in cls._builder_map
        ]
        if missing_parts:
            raise ValueError(
                f"{cls.__name__}._builder_map missing parts: {missing_parts}"
            )

    def __init__(self, dimension_data: DimensionData):
        self._dimension_data = dimension_data
        self._solid_cache = {}

    def build_part(
        self, part_type: Enum, cached_solid: bool = False
    ) -> cq.Workplane | cq.Solid:
        """
        Given a part type (an Enum member), builds and returns the corresponding
        cadquery object.

        If cached_solid is False (default), returns a Workplane object.
        If cached_solid is True, returns a Solid object (cached for performance).
        """
        try:
            build_func = self._builder_map[part_type]
        except KeyError as exc:
            raise ValueError(
                f"Invalid part type: {part_type}. "
                f"Available parts: {list(self._builder_map.keys())}"
            ) from exc

        if cached_solid:
            func_name = build_func.__name__
            if not func_name in self._solid_cache:
                self._solid_cache[func_name] = build_func(self).val()
            return self._solid_cache[func_name]

        return build_func(self)

    def clear_cache(self) -> None:
        """Clear the solid cache if needed."""
        self._solid_cache.clear()

    @classmethod
    def get_part(
        cls,
        dimension_data: DimensionData,
        part_type: Enum,
        *builder_args,
        **builder_kwargs,
    ) -> cq.Workplane:
        """
        Convenience method to build a single part directly without manually instantiating
        a Builder instance.

        Args:
            dimension_data (DimensionData): The dimension data for the builder.
            part_type (Enum): The part type to build.
            *builder_args: Positional arguments forwarded to the Builder constructor.
            **builder_kwargs: Keyword arguments forwarded to the Builder constructor.

        Returns:
            cadquery.Workplane: The built part as a Workplane object.
        """
        builder = cls(dimension_data, *builder_args, **builder_kwargs)
        return builder.build_part(part_type)

    @staticmethod
    def register(part_type: Enum) -> Callable:
        def decorator(func):
            # Defer attaching into _builder_map until __init_subclass__
            func._registered_part_type = part_type
            return func

        return decorator


class AssemblerABC(DimensionDataMixin, ABC):
    """
    To be used as a base class for all assemblers.
    Subclasses must implement the following:

    1. Define the following class attributes:
       - _BuilderClass: A concrete Builder class that inherits from BuilderABC.
         (Note: although these attribute names begin with an underscore,
         they must be explicitly defined in each subclass.)

    2. If additional instance variables are needed, implement a custom __init__ method.
       The __init__ method must accept dimension_data: DimensionData as its first argument,
       and must call super().__init__(dimension_data) before adding custom logic.

    3. Implement the get_metadata_map method.
       It must return a dictionary mapping part types (builder.PartTypeEnum members)
       to metadata dictionaries containing keyword arguments for the cq.Assembly.add method.
    """

    _BuilderClass: type[BuilderABC]  # Subclasses need to assign this.
    _PartEnum: type[Enum]  # Subclasses need to assign this.

    # Subclasses must define if cls._PartEnum is not cls._BuilderClass._PartTypeEnum
    _part_type_map: dict[Enum, Enum]

    @property
    def PartEnum(self) -> type[Enum]:  # pylint: disable=invalid-name
        return self._PartEnum

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Validate cls._BuilderClass
        if not hasattr(cls, "_BuilderClass"):
            raise TypeError(f"{cls.__name__} must define _BuilderClass.")
        if not issubclass(cls._BuilderClass, BuilderABC):
            raise TypeError(
                f"{cls.__name__}._BuilderClass must inherit from BuilderABC."
            )

        # Validate cls._PartEnum
        if not hasattr(cls, "_PartEnum"):
            raise TypeError(f"{cls.__name__} must define _PartEnum.")
        if not issubclass(cls._PartEnum, Enum):
            raise TypeError(f"{cls.__name__}._PartEnum must be an Enum.")

        if cls._PartEnum is cls._BuilderClass._PartTypeEnum:
            if hasattr(cls, "_part_type_map"):
                raise ValueError(
                    "No need to manually define '_part_type_map' when "
                    f"{cls.__name__}._PartEnum is {cls._BuilderClass.__name__}._PartTypeEnum"
                )
            cls._part_type_map = {member: member for member in cls._PartEnum}
            return  # Dont need to validate keys member below when assigned this way.

        # Validate cls._part_type_map data structure
        if not hasattr(cls, "_part_type_map"):
            raise TypeError(f"{cls.__name__} must define _part_type_map.")
        if not isinstance(cls._part_type_map, dict):
            raise TypeError(f"{cls.__name__}._part_type_map must be a dictionary.")

        # Validate keys of cls._part_type_map
        actual_keys = set(cls._part_type_map.keys())
        expected_keys = set(cls._PartEnum)
        if actual_keys != expected_keys:
            raise ValueError(
                f"Incomplete/Erroneous mapping of cls._PartEnum:\n"
                f"Expected the following PartEnum keys:\n{expected_keys}\n"
                f"Got the following keys:\n{actual_keys}"
            )

        # Validate values of cls._part_type_map
        actual_values = set(cls._part_type_map.values())
        allowed_values = set(cls._BuilderClass._PartTypeEnum)
        non_part_type_values = actual_values - allowed_values
        if non_part_type_values:
            raise ValueError(
                f"Only allowed to map to the following part types:\n{allowed_values}\n"
                f"Got the following 'forbidden' part types:\n{non_part_type_values}"
            )

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
            assembly_parts (Iterable[Enum]): Iterable of part (PartEnum members)
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

            part_type = self._part_type_map[part]
            cq_solid = self.builder.build_part(part_type, cached_solid=True)
            assembly_data.append((cq_solid, metadata))
        return assembly_data

    def assemble(self, assembly_parts: Iterable[Enum] | None = None) -> cq.Assembly:
        assembly_parts = assembly_parts or tuple(self.PartEnum)
        assembly = cq.Assembly()
        for cq_solid, metadata in self._get_assembly_data(assembly_parts):
            assembly.add(cq_solid, **metadata)
        return assembly

    @classmethod
    def get_assembly(
        cls,
        dimension_data: DimensionData,
        *assembler_args,
        assembly_parts: Iterable[Enum] | None = None,
        **assembler_kwargs,
    ) -> cq.Assembly:
        """
        Convenience method to create an assembly directly without manually instantiating
        an Assembler instance.

        Args:
            dimension_data (DimensionData): The dimension data for the assembly.
            *assembler_args: Positional arguments forwarded to the Assembler constructor.
            assembly_parts (Iterable[Enum], optional): Parts (members of self.PartEnum) to include. Defaults to all parts.
            **assembler_kwargs: Keyword arguments forwarded to the Assembler constructor.

        Returns:
            cadquery.Assembly: The assembled cadquery Assembly object.
        """
        assembler = cls(dimension_data, *assembler_args, **assembler_kwargs)
        return assembler.assemble(assembly_parts=assembly_parts)
