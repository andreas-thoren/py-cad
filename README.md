![Python](https://img.shields.io/badge/python-3.10--3.12-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
# py-cad

**A modular and extensible parametric CAD framework for Python using CadQuery.**

`py-cad` provides a clean architecture for defining 3D parts, managing dimensions per part type, and assembling models using CadQuery. It emphasizes code reuse, clarity, and separation of concerns.

---

## Design Philosophy

All **part names** and **metadata keys** are normalized to lowercase strings internally.
**Both `str` and `StrAutoEnum`** (or other string-like enums) are accepted in external APIs and project definitions. Use of **`StrAutoEnum`** with `auto()` as values is recommended.

---

## 📦 Installation

```bash
git clone https://github.com/andreas-thoren/py-cad.git
cd py-cad
pip install .
```

> Ensure the package is installed for imports and tests to function correctly. This package is not currently published on PyPI. It must be installed locally from source.

---

## 🚀 Full Usage Example

This example demonstrates a complete setup using enums, dimension logic, part builders, and an assembler.

> All code can be kept in a single file or organized across modules.

### ▶️ Define parts, part types, part_type_map and project variables

Define:

* **`Part`** — all unique parts in the assembly (`StrAutoEnum` or iterable of strings)
* **`PartType`** — unique part templates
* **`PART_TYPE_MAP`** — mapping from `Part` to `PartType`

```python
from enum import auto
from py_cad import StrAutoEnum

class Part(StrAutoEnum):
    BOTTOM = auto()
    LONG_SIDE = auto()
    LONG_SIDE_INVERSE = auto()
    SHORT_SIDE = auto()
    SHORT_SIDE_INVERSE = auto()
    TOP = auto()

class PartType(StrAutoEnum):
    BOTTOM = auto()
    LONG_SIDE_PANEL = auto()
    SHORT_SIDE_PANEL = auto()
    TOP = auto()

PART_TYPE_MAP = {
    Part.BOTTOM: PartType.BOTTOM,
    Part.LONG_SIDE: PartType.LONG_SIDE_PANEL,
    Part.LONG_SIDE_INVERSE: PartType.LONG_SIDE_PANEL,
    Part.SHORT_SIDE: PartType.SHORT_SIDE_PANEL,
    Part.SHORT_SIDE_INVERSE: PartType.SHORT_SIDE_PANEL,
    Part.TOP: PartType.TOP,
}

class Material(StrAutoEnum):
    PLYWOOD = auto()
    SOLID_WOOD = auto()

MATERIAL_THICKNESS_MAP = {
    Material.PLYWOOD: 9,
    Material.SOLID_WOOD: 12,
}

PART_TYPE_MATERIAL_MAP = {
    PartType.BOTTOM: Material.PLYWOOD,
    PartType.LONG_SIDE_PANEL: Material.SOLID_WOOD,
    PartType.SHORT_SIDE_PANEL: Material.SOLID_WOOD,
    PartType.TOP: Material.SOLID_WOOD,
}

PART_TYPE_THICKNESS_MAP = {
    pt: MATERIAL_THICKNESS_MAP[mat]
    for pt, mat in PART_TYPE_MATERIAL_MAP.items()
}

ROUTE_DEPTH = MATERIAL_THICKNESS_MAP[Material.SOLID_WOOD] / 2
```

**Note:**
You can also use an iterable of plain strings for `Part`/`PartType` and the corresponding strings for `PART_TYPE_MAP`.
If all your parts have a unique template, just omit `part_types` and `PART_TYPE_MAP` and use Part both for the Builder (when using @BuilderABC.register(...)) and Assembler (as keys in get_metadata_map).

---

### ▶️ DimensionData Subclassing and instantiation

`DimensionData` enables managing global dimensions **alongside part-specific dimensions and attributes**.
Subclassing it allows you to define additional dimension logic for individual part types in your CAD assemblies.

A typical subclass involves:

#### 1. Custom `__init__`

* Sets additional calculated dimensions or variables.
* Calls `super().__init__(basic_dimensions, part_type_attributes, ...)` to initialize core dimension data.
* `part_type_attributes` allows setting custom attributes (e.g., material thickness, hole diameter) that vary per part type.

#### 2. Implementing `get_part_types_dimensions`

* Defines the explicit dimensions (and optional additional attributes) for each part type.
* Must return a dictionary mapping each `part_type` (string or enum) to either:

  * A simple `(x_len, y_len, z_len)` tuple.
  * A tuple containing `(x_len, y_len, z_len)` plus a dictionary of additional named dimensions.

**Note:**
For simple projects subclassing DimensionData is not always needed. In those cases just create an instance of DimensionData directly.

```python
from py_cad import DimensionData

class BoxDimensionData(DimensionData):
    def __init__(self, x_len, y_len, z_len, mat_thickness, route_depth=0.0):
        part_type_attributes = {"mat_thickness": mat_thickness}
        super().__init__((x_len, y_len, z_len), part_type_attributes)
        self.route_depth = route_depth
        self.routed_x_len = mat_thickness[PartType.SHORT_SIDE_PANEL] - route_depth
        self.routed_y_len = mat_thickness[PartType.LONG_SIDE_PANEL] - route_depth
        self.routed_z_len = mat_thickness[PartType.TOP] - route_depth
        self.panel_z_len = z_len - self.routed_z_len

    def get_part_types_dimensions(self):
        panel_y = self.y_len - 2 * self.routed_y_len
        btm_x = self.x_len - 2 * self.routed_x_len
        btm_z = self[PartType.BOTTOM].mat_thickness
        top_z = self[PartType.TOP].mat_thickness
        long_th = self[PartType.LONG_SIDE_PANEL].mat_thickness
        short_th = self[PartType.SHORT_SIDE_PANEL].mat_thickness

        return {
            PartType.BOTTOM: (btm_x, panel_y, btm_z),
            PartType.LONG_SIDE_PANEL: (self.x_len, long_th, self.panel_z_len),
            PartType.SHORT_SIDE_PANEL: (short_th, panel_y, self.panel_z_len),
            PartType.TOP: (self.x_len, self.y_len, top_z),
        }

BOX_DIMENSIONS = BoxDimensionData(
    400, 200, 200, PART_TYPE_THICKNESS_MAP, route_depth=ROUTE_DEPTH
)
```

#### 🔍 Accessing Per-Part-Type Dimensions and Attributes

Once initialized, all dimensions and attributes per part type can be accessed like a dictionary:

```python
dim_data = MyDimensionData(...)
length = dim_data["my_part_type"].x_len
thickness = dim_data["my_part_type"].material_thickness
```

This applies to:

* Dimensions returned via `get_part_types_dimensions`
* Attributes defined via `part_type_attributes`

---

### ▶️ Builder Definition

Subclass `BuilderABC`: 

* Define a **build method for each part type**. Register each method with `@BuilderABC.register(...)`.
* A custom __init__ is usually not needed since dimensions should primarily be added to the DimensionData instance and not the builder instance.

```python
import cadquery as cq
from py_cad import BuilderABC

class Builder(BuilderABC):
    @BuilderABC.register(PartType.LONG_SIDE_PANEL)
    def get_long_side_panel(self):
        long = self.dim[PartType.LONG_SIDE_PANEL]
        bottom_thickness = self.dim[PartType.BOTTOM].z_len
        offset = self.dim.x_len / 2 - long.y_len / 2
        return (
            cq.Workplane("XY")
            .box(long.x_len, long.y_len, long.z_len)
            .faces("<Y").workplane()
            .pushPoints([(offset, 0), (-offset, 0)])
            .rect(long.y_len, long.z_len).cutBlind(-self.dim.route_depth)
            .faces("<Y").workplane()
            .moveTo(0, -(long.z_len - bottom_thickness) / 2)
            .rect(self.dim.x_len, bottom_thickness).cutBlind(-self.dim.route_depth)
        )

    @BuilderABC.register(PartType.SHORT_SIDE_PANEL)
    def get_short_side_panel(self):
        short = self.dim[PartType.SHORT_SIDE_PANEL]
        bottom_thickness = self.dim[PartType.BOTTOM].z_len
        return (
            cq.Workplane("XY")
            .box(short.x_len, short.y_len, short.z_len)
            .faces("<X").workplane()
            .moveTo(0, -(short.z_len - bottom_thickness) / 2)
            .rect(short.y_len, bottom_thickness).cutBlind(-self.dim.route_depth)
        )

    @BuilderABC.register(PartType.BOTTOM)
    def get_bottom(self):
        btm = self.dim[PartType.BOTTOM]
        return cq.Workplane("XY").box(btm.x_len, btm.y_len, btm.z_len)

    @BuilderABC.register(PartType.TOP)
    def get_top(self):
        top = self.dim[PartType.TOP]
        return (
            cq.Workplane("XY")
            .box(self.dim.x_len, self.dim.y_len, top.z_len - self.dim.route_depth)
            .faces(">Z").workplane()
            .rect(
                self.dim.x_len - top.z_len * 2,
                self.dim.y_len - top.z_len * 2,
            ).extrude(self.dim.route_depth)
        )
```

---

### ▶️ Assembler Definition

Subclass `AssemblerABC`:

* Set `BuilderClass` to your builder class
* Set `part_map` (mapping part → part_type; omit if 1:1)
* Implement `get_metadata_map` which should return a mapping with parts as keys and dicts with keyword arguments for cq.Assembly().add as values. If name or color are not specified for a part, default values will be used automatically.
* __init__ can optionally be provided as per below. Remember to call super().__init__(dim).

```python
import cadquery as cq
from py_cad import AssemblerABC

class Assembler(AssemblerABC):
    BuilderClass = Builder
    part_map = PART_TYPE_MAP # Can be skipped if Part is PartType

    def __init__(self, dim, visual_offset=0):
        super().__init__(dim)
        btm_z = self.dim[PartType.BOTTOM].z_len
        self.assy_dst_x = self.dim.x_len / 2 + visual_offset - self.dim.routed_x_len
        self.assy_dst_y = self.dim.y_len / 2 + visual_offset - self.dim.routed_y_len
        self.assy_dst_bottom = (self.dim.panel_z_len - btm_z) / 2
        self.assy_dst_top = visual_offset + self.dim.z_len / 2

    def get_metadata_map(self):
        return {
            Part.BOTTOM: {"loc": cq.Location((0, 0, -self.assy_dst_bottom))},
            Part.LONG_SIDE: {"loc": cq.Location((0, self.assy_dst_y, 0))},
            Part.LONG_SIDE_INVERSE: {
                "loc": cq.Location((0, -self.assy_dst_y, 0), (0, 0, 1), 180)
            },
            Part.SHORT_SIDE: {"loc": cq.Location((self.assy_dst_x, 0, 0))},
            Part.SHORT_SIDE_INVERSE: {
                "loc": cq.Location((-self.assy_dst_x, 0, 0), (0, 0, 1), 180)
            },
            Part.TOP: {
                "loc": cq.Location((0, 0, self.assy_dst_top), (1, 0, 0), 180)
            },
        }
```

---

### ▶️ Build and Display

```python
assembler = Assembler(BOX_DIMENSIONS)
assembly = assembler.assemble()
show_object(assembly, "basic_box") # If using CQ-editor
```

---

## 📊 Framework Flow Overview

```text
Part / PartType
      │
      ▼
DimensionData (or subclass)
      │
      ▼
BuilderABC (subclass)
      │
      ▼
AssemblerABC (subclass)
      │
      ▼
assembler = Assembler(...)
assembly = assembler.assemble()  # returns cq.Assembly
show_object(assembly, "my_assembly") # If using CQ-editor
```

---

## 🔧 Developer Notes

* Use of `StrAutoEnum` for parts and part types is highly recommended even if plain iterable of strings work.
* You **must subclass** `BuilderABC` and `AssemblerABC`.
* Primitives are optional: if used, concrete builder/assembler classes may already exist.

---

## Advanced Features

* **Subclasses:** You can subclass `DimensionData` if you need more fields for your project.
* **Inheritance:** Builder and Assembler classes support inheritance; all attributes are internally normalized and resolved. Parent build methods are accessible from builder subclasses. Assembly metadata provided in parent assemblers are also accessible in child assemblers. If same part or part type is defined in child and parent child definition takes precedence.
* **Error messages:** If mappings are incomplete or inconsistent, detailed error messages are provided at class creation time.

---

## 📝 License

MIT

---

## Contributing

Feel free to fork and adapt the models for your own projects.
Feedback, issues, and pull requests are welcome!

---

## TODO

* AssemblerABC should accept constraints.
* Add more complete readme explanation of how inheritance works.
* Add included_parts and excluded_parts to AssemblerABC to specify which fields to inherit.
* Add class-level descriptors to signal configuration-only attributes after subclass creation

---

**Happy sketching!**
— Andreas (Author)

---