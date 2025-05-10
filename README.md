# Athor Sketches

Repository containing my CadQuery sketches and designs, primarily intended for woodworking and related projects.

---

## Creating a New Project

Follow these steps to create a new CadQuery project using the shared model framework defined in `helpers/models.py`.

Each project directory (e.g., `garbage_sort_box/`) typically contains:

* `project_data.py` — dimensions, enums, and part mappings
* `parts.py` — subclass of `BuilderABC` for generating parts
* `assembly.py` — subclass of `AssemblerABC` for combining parts

Typical project structure:
```text
your_project
├── assembly.py
├── parts.py
├── project_data.py
```

---

### Step 1: Define Part, PartType, and optionally PART_TYPE_MAP; create a DimensionData instance

In `project_data.py`, define:

* `Part` (StrEnum) — unique parts used in the final assembly (may include mirrored or variant instances)
* `PartType` (StrEnum) — distinct shape templates needed to build those parts
* `PART_TYPE_MAP` (dict[Part, PartType]) — Can be defined here or directly at the _part_type_map of the AssemblerABC subclass definition.

```python
from enum import StrEnum, auto
from helpers.models import DimensionData

class Part(StrEnum):
    BOTTOM = auto()
    LEFT_SIDE = auto()
    RIGHT_SIDE = auto()

class PartType(StrEnum):
    BOTTOM = auto()
    SIDE_PANEL = auto()

PART_TYPE_MAP = {
    Part.BOTTOM: PartType.BOTTOM,
    Part.LEFT_SIDE: PartType.SIDE_PANEL,
    Part.RIGHT_SIDE: PartType.SIDE_PANEL,
}

DIMENSION_DATA = DimensionData(x_length=400, y_length=300, z_length=250, material_thickness=12)
```
For advanced customization, you may subclass `DimensionData` if extra dimension fields are needed.

💡 If your project has a 1-to-1 mapping between `Part` and `PartType`, you may skip `PartType` and `PART_TYPE_MAP` and assign `Part` to both `_PartEnum` (AssemblerABC subclass) and `_PartTypeEnum` (BuilderABC subclass) in which case identity mapping is applied automatically by the assembler.

---

### Step 2: Define a Builder Subclass

In `parts.py`, subclass `BuilderABC` and define one method per `PartType`. Register each build method using the `@BuilderABC.register(...)` decorator.

```python
import cadquery as cq
from helpers.models import BuilderABC, DimensionData
from .project_data import PartType

class Builder(BuilderABC):
    _PartTypeEnum = PartType

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

Thanks to `DimensionDataMixin`, you can access dimension values (`self.x_length`, `self.z_offset`, etc.), from the DimensionData instance directly in BuilderABC subclasses.

---

### Step 3: Define an Assembler Subclass

In `assembly.py`, subclass `AssemblerABC`. Specify:

* `_BuilderClass` — the builder class you just created
* `_PartEnum` — your `Part` enum
* `_part_type_map` — mapping from `Part` to `PartType` (omit if 1-to-1 mapping, see Step 1)

You must also implement `get_metadata_map`, which controls placement and metadata of parts in the final assembly.

```python
import cadquery as cq
from helpers.models import AssemblerABC, DimensionData
from .parts import Builder
from .project_data import Part, PART_TYPE_MAP

class Assembler(AssemblerABC):
    _BuilderClass = Builder
    _PartEnum = Part
    _part_type_map = PART_TYPE_MAP.copy()

    def __init__(self, dimension_data: DimensionData):
        super().__init__(dimension_data)
        self.x_offset = self.x_length / 2
        self.z_offset = self.z_length / 2

    def get_metadata_map(self) -> dict[Part, dict]:
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

Thanks to `DimensionDataMixin`, you can access dimension values (`self.x_length`, `self.z_offset`, etc.), from the DimensionData instance directly in AssemblerABC subclasses.

---

### Step 4: Visualize in CadQuery

To preview your parts or the full assembly:

```python
from projects.my_box.project_data import DIMENSION_DATA
from projects.my_box.parts import Builder, Part
from projects.my_box.assembly import Assembler

# Show a single part
show_object(Builder.get_part(DIMENSION_DATA, Part.BOTTOM), name="Bottom")

# Show entire assembly
show_object(Assembler.get_assembly(DIMENSION_DATA), name="Full Assembly")
```

---

## Project Setup (Python Environment)

Follow these instructions to set up your Python virtual environment correctly for working with this repository.

### Step 1: Create a virtual environment

Use Python ≥3.9 and <3.13 (currently using 3.12):

```bash
python3.12 -m venv .venv
```

### Step 2: Activate the environment

* **macOS/Linux**

```bash
source .venv/bin/activate
```

* **Windows (PowerShell)**

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Upgrade pip

```bash
pip install --upgrade pip
```

### Step 4: Install the project in editable mode

(This reads `pyproject.toml` and installs dependencies.)

```bash
pip install -e .
```

### Step 5: Verify the installation

```bash
python --version    # Should display 3.12.x
pip list            # Should list cadquery, CQ-editor, etc.
```
