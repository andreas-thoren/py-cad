# Athor Sketches

Repository containing my CadQuery sketches and designs, primarily intended for woodworking and related projects.

## Creating a New Project

Follow these steps to start a new concrete CadQuery project in this repository. Each project will clearly follow this structure to maintain consistency and ease of development.

### Step 1: Define a `PartType` Enum

Create a new directory for your project under the `projects/` folder. Inside this folder, create `parts.py` and define your `PartType` enum clearly:

```python
# projects/<your_project>/parts.py
from enum import Enum, auto

class PartType(Enum):
    BOTTOM = auto()
    SIDE_PANEL = auto()
    TOP_PANEL = auto()
```

### Step 2: Decide on Dimension Data

In the same project directory, decide if the basic `DimensionData` class (from `helpers.models`) is sufficient, or if your project requires additional dimensions.

* **If basic dimensions (`x_length`, `y_length`, `z_length`, `material_thickness`) are enough**, simply create an instance of `DimensionData` directly:

```python
# projects/<your_project>/measurements.py
from helpers.models import DimensionData

DIMENSION_DATA = DimensionData(
    x_length=400,
    y_length=300,
    z_length=200,
    material_thickness=12
)
```

* **If additional dimensions are required**, subclass `DimensionData`:

```python
# projects/<your_project>/measurements.py
from helpers.models import DimensionData
from dataclasses import dataclass

@dataclass
class MyProjectDimensions(DimensionData):
    extra_clearance: float = 5.0

DIMENSION_DATA = MyProjectDimensions(
    x_length=400,
    y_length=300,
    z_length=200,
    material_thickness=12,
    extra_clearance=5.0
)
```

### Step 3: Create Your Builder Class

Subclass `BuilderABC` in your `parts.py`. Define methods to build each part:

```python
# projects/<your_project>/parts.py
from functools import cached_property
from helpers.models import BuilderABC
import cadquery as cq

class MyProjectBuilder(BuilderABC):

    def __init__(self, dimension_data):
        super().__init__(dimension_data) # Call super init first
        # Additional instance variables like calculated dimensions can be defined here directly

    @cached_property
    def _part_build_map(self): # This property needs to be defined on all subclasses
        return {
            PartType.BOTTOM: (self.build_bottom, (), {}),
            PartType.SIDE_PANEL: (self.build_side_panel, (), {}),
        }

    def build_bottom(self):
        return cq.Workplane("XY").box(self.x_length, self.y_length, self.material_thickness)

    def build_side_panel(self):
        return cq.Workplane("XZ").box(self.x_length, self.z_length, self.material_thickness)
```

### Step 4: Create Your Assembler Class

Subclass `AssemblerABC` in `assembly.py` to handle part placement and assembly logic:

```python
# projects/<your_project>/assembly.py
from helpers.models import AssemblerABC
import cadquery as cq
from .parts import PartType, MyProjectBuilder

class MyProjectAssembler(AssemblerABC):

    _PartTypeEnum = PartType
    _BuilderClass = MyProjectBuilder

    def __init__(self, dimension_data):
        super().__init__(dimension_data) # Call super init first
        # Additional instance variables like calculated offsets can be defined here directly

    def get_metadata_map(self): # This method needs to be defined on all subclasses.
        return {
            PartType.BOTTOM: {
                "loc": cq.Location((0, 0, 0)),
                "color": cq.Color("tan"),
            },
            PartType.SIDE_PANEL: {
                "loc": cq.Location((self.x_length / 2, 0, self.z_length / 2)),
                "color": cq.Color("brown"),
            },
        }
```

Thanks to the `DimensionDataMixin`, you automatically gain direct access to all attributes defined in your `DimensionData` (and its subclasses) from within both your Builder and Assembler subclasses. For further detailed requirements of the Builder and Assembler subclasses, please consult their respective docstrings (`BuilderABC` and `AssemblerABC` in `helpers/models.py`).

### Step 5: Visualize Parts and Assemblies with CadQuery
You can easily visualize parts and entire assemblies using CadQuery's `show_object` function:

```python
# Example visualization script
import cadquery as cq
from projects.<your_project>.measurements import DIMENSION_DATA
from projects.<your_project>.assembly import MyProjectAssembler
from projects.<your_project>.parts import MyProjectBuilder, PartType

# Visualize a single part
part = MyProjectBuilder.get_part(DIMENSION_DATA, PartType.BOTTOM)
show_object(part, name="Bottom Part")

# Visualize the entire assembly
assembly = MyProjectAssembler.get_assembly(DIMENSION_DATA)
show_object(assembly, name="Full Assembly")
```

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
