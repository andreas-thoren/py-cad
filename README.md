# Athor Sketches

Repository containing my CadQuery sketches and parametric designs, primarily intended for woodworking and related projects.
All projects use a shared, extensible part/assembly model defined in `helpers/models.py`.

---

## Design Philosophy

All **part names** and **metadata keys** are normalized to lowercase strings internally.
**Both `str` and `StrEnum`** (or other string-like enums) are accepted in external APIs and project definitions.
This approach allows projects to choose the most readable and maintainable interface, while ensuring robust internal handling.

---

## Project Structure

A typical project directory (e.g., `garbage_sort_box/`) contains:

```
your_project/
├── project_data.py    # Defines enums/part names, dimension data, mappings
├── parts.py           # Subclass of BuilderABC for part generation
└── assembly.py        # Subclass of AssemblerABC for assembly logic
```

---

## Getting Started: Creating a New Project

### 1. Define Parts, Part Types, and Dimensions

In `project_data.py`, define:

* **`Part`** — all unique parts in the assembly (`StrEnum` or list of strings)
* **`PartType`** — unique part templates (can be same as `Part` if 1:1)
* **`PART_MAP`** — mapping from `Part` to `PartType` (omit if 1:1)
* **`DIMENSION_DATA`** — a `DimensionData` instance (subclass if you need more fields)

**Example:**

```python
from enum import StrEnum
from helpers.models import DimensionData

class Part(StrEnum):
    BOTTOM = "bottom"
    LEFT_SIDE = "left_side"
    RIGHT_SIDE = "right_side"

class PartType(StrEnum):
    BOTTOM = "bottom"
    SIDE_PANEL = "side_panel"

PART_MAP = {
    Part.BOTTOM: PartType.BOTTOM,
    Part.LEFT_SIDE: PartType.SIDE_PANEL,
    Part.RIGHT_SIDE: PartType.SIDE_PANEL,
}

DIMENSION_DATA = DimensionData(
    x_length=400, y_length=300, z_length=250, material_thickness=12
)
```

**Note:**
You can also use an interable of plain strings for `Part`/`PartType` and the corresponding strings for `PART_MAP`.
If all your parts have a unique template, just set `parts` and `part_types` to the same StrEnum class (or Iterable) and skip `PART_MAP`.

---

### 2. Implement the Builder

In `parts.py`, subclass `BuilderABC` and define a **build method for each part type**.
Register each method with `@BuilderABC.register(...)`.

**Example:**

```python
import cadquery as cq
from helpers.models import BuilderABC, DimensionData
from .project_data import PartType

class Builder(BuilderABC):
    part_types = PartType

    def __init__(self, dimension_data: DimensionData):
        super().__init__(dimension_data)
        self.offset = self.material_thickness / 2

    @BuilderABC.register(PartType.BOTTOM)
    def build_bottom(self) -> cq.Workplane:
        return cq.Workplane("XY").box(self.x_length, self.y_length, self.material_thickness)

    @BuilderABC.register(PartType.SIDE_PANEL)
    def build_side_panel(self) -> cq.Workplane:
        return cq.Workplane("XZ").box(self.x_length, self.z_length, self.material_thickness)
```

You can access dimension values (`self.x_length`, `self.z_length`, etc.) directly, thanks to `DimensionDataMixin`.

---

### 3. Implement the Assembler

In `assembly.py`, subclass `AssemblerABC`:

* Set `BuilderClass` to your builder class
* Set `parts` (your `Part` enum or list of strings)
* Optionally set `part_map` (mapping part → part\_type; omit if 1:1)
* Implement `get_metadata_map` (placement/color/etc for each part)

**Example:**

```python
import cadquery as cq
from helpers.models import AssemblerABC, DimensionData
from .parts import Builder
from .project_data import Part, PART_MAP

class Assembler(AssemblerABC):
    BuilderClass = Builder
    parts = Part
    part_map = PART_MAP  # Omit if parts == part_types

    def __init__(self, dimension_data: DimensionData):
        super().__init__(dimension_data)
        self.x_offset = self.x_length / 2
        self.z_offset = self.z_length / 2

    def get_metadata_map(self) -> dict:
        return {
            Part.BOTTOM: {
                "loc": cq.Location((0, 0, 0)),
                "color": cq.Color("tan"),
            },
            Part.LEFT_SIDE: {
                "loc": cq.Location((-self.x_offset, 0, self.z_offset)),
                "color": cq.Color("burlywood"),
            },
            Part.RIGHT_SIDE: {
                "loc": cq.Location((self.x_offset, 0, self.z_offset)),
                "color": cq.Color("burlywood"),
            },
        }
```

If your project has a **1:1 mapping** between parts and part types, just omit `part_map` and set parts = PartType.
Thanks to `DimensionDataMixin`, you can access dimension values (`self.x_length`, `self.z_offset`, etc.), from the DimensionData instance directly in AssemblerABC subclasses.

---

### 4. Visualize Your Model in CadQuery

Preview parts or assemblies using `show_object`:

```python
from projects.my_box.project_data import DIMENSION_DATA, Part
from projects.my_box.parts import Builder
from projects.my_box.assembly import Assembler

# Show a single part
show_object(Builder.get_part(DIMENSION_DATA, Part.BOTTOM), name="Bottom")

# Show the full assembly
show_object(Assembler.get_assembly(DIMENSION_DATA), name="Full Assembly")
```

---

## Project Setup

### 1. Create a Virtual Environment

Use Python 3.9–3.12:

```bash
python3.12 -m venv .venv
```

### 2. Activate the Environment

* **macOS/Linux:**
  `source .venv/bin/activate`
* **Windows (PowerShell):**
  `.\.venv\Scripts\Activate.ps1`

### 3. Upgrade pip

```bash
pip install --upgrade pip
```

### 4. Install in Editable Mode

```bash
pip install -e .
```

### 5. Verify

```bash
python --version    # Should be 3.12.x
pip list            # Should include cadquery, etc.
```

---

## Advanced Tips

* **Subclasses:** You can subclass `DimensionData` if you need more fields for your project.
* **Strings or Enums:** All parts, part types, and mappings may be defined as plain strings or as `StrEnum` members.
* **Inheritance:** Builder and Assembler classes support inheritance; all attributes are internally normalized and resolved.
* **Error messages:** If mappings are incomplete or inconsistent, detailed error messages are provided at class creation time.

---

## Contributing

Feel free to fork and adapt the models for your own projects.
Feedback, issues, and pull requests are welcome!

---

## TODO

* Add stricter normalization collision checks in `ResolveMixin`
* Add class-level descriptors to signal configuration-only attributes after subclass creation
* Normalize all external API methods to accept both `str` and `StrEnum` for maximum flexibility

---

**Happy sketching!**
— Andreas (Athor)

---