# Code Review

Generated 2026-04-30. Items already completed (deleted broken root scripts, fixed `man_testing.py`) are removed. Work through this top-down: high-impact bugs first, then architectural friction, then cleanup.

---

## Bottom line

For a hobby project built a year ago to simplify CadQuery for woodworking, this is **better than it has any right to be**. The framework is real — it would survive being pulled into a separate package and used for non-woodworking parametric assemblies without major rework.

**Strengths worth preserving:**
- Clean four-axis abstraction: `Part` (instances) / `PartType` (templates) / `DimensionData` (sizes) / `Builder`+`Assembler` (geometry vs placement)
- The registration pattern (`@BuilderABC.register` walked by `__init_subclass__`) is genuinely well-designed
- Diamond-inheritance support via `InheritanceMixin` works and is tested (`tests/test_project/assembly.py`)
- 43 tests covering hard cases: multi-level inheritance resolution, `NormalizedDict` semantics, freeze-after-init, both tuple shapes from `get_part_types_dimensions`
- `NormalizedDict` quietly hides a class of bugs (case/whitespace mismatches between enum values and string keys)
- Type hints throughout, docstrings explain *why* not just *what*

The quality gap between `src/py_cad/` (carefully designed, well-tested) and the repo periphery (broken/abandoned scripts, naming sprawl) is the most visible problem; the framework itself is solid.

---

## Priority 1 — Real bugs (silent, fix soon)

### [x] `BuilderABC.build_part` strips arguments — dead `invert_grooves` parameter

**Resolution (2026-04-30):** Picked Option B — dropped the dead args. Per the framework's design intent, a part is built one specific way; if a near-duplicate variant is needed in the future, register a separate method that internally calls the first with arguments. This keeps `build_part` simple (no `*args/**kwargs` forwarding) and avoids the cache-keying complications that forwarding would introduce.

Files touched:
- `src/py_cad/primitives/plywood_box/parts.py` — removed `invert_grooves` from `get_long_side_panel`, inlined `groove_face = "<Y"`
- `projects/garbage_sort_box/parts.py` — same

---

### [ ] `set_basic_dimensions` doesn't reject strings

**Where:** `src/py_cad/core.py:76-79`

```python
if not isinstance(basic_dimensions, Sequence) or len(basic_dimensions) != 3:
    raise TypeError(...)
```

A 3-character string is a `Sequence` of length 3. `BasicDimensionData("abc")` would silently set `x_len="a"`, `y_len="b"`, `z_len="c"` and pass validation.

**Fix:** add `or isinstance(basic_dimensions, str)` to the check, or check that each element is a number:

```python
if (
    not isinstance(basic_dimensions, Sequence)
    or isinstance(basic_dimensions, str)
    or len(basic_dimensions) != 3
    or not all(isinstance(d, (int, float)) for d in basic_dimensions)
):
    raise TypeError(...)
```

---

## Priority 2 — Misleading code (no incorrect behavior, but readers will trip)

### [ ] Dead test assertion in `test_dimension_data.py:18`

```python
def test_frozen_after_init(self):
    data = BasicDimensionData((1, 2, 3), freeze=True)
    self.new_attribute = 42  # Allowed adding new attributes  ← self is TestCase, not data
    with self.assertRaises(AttributeError):
        data.x_len = 5
```

The assertion below it (`data.x_len = 5` raises) does test the right thing, but line 18 sets an attribute on the `TestCase` instance, not on `data`. The comment misleads. Either delete line 18 or change to `data.new_attribute = 42` (which should NOT raise, since you can add new attrs after freeze if they didn't exist before — verify the intent first).

---

### [ ] `older_parent_items` is misnamed in `helpers.py:71-82`

In `InheritanceMixin.get_parent_items`, the variable `older_parent_items` is set on the first iteration to the *youngest* parent (`cls.__mro__[1]` = immediate parent). It only becomes "older" in iterations 2+. The name confused me when reading; rename to `current_base_items` or just `base_items`.

```python
for base in cls.__mro__[1:]:
    base_items = getattr(base, attr_name, None)
    if base_items is None:
        continue
    if parent_items is None:
        parent_items = base_items
    else:
        parent_items = base_items | parent_items  # younger overrides older
```

---

### [ ] `AssemblerABC` docstring numbers requirements 1, 3, 4 (skips 2)

**Where:** `src/py_cad/core.py:341-356`

Cosmetic but jarring. Renumber to 1, 2, 3.

---

### [ ] `tests/test_normalized_dict.py:2` imports from wrong module

```python
from py_cad.core import NormalizedDict   # works because core re-imports from helpers
```

Canonical path is `from py_cad.helpers import NormalizedDict`. Fragile if you ever clean up `core.py`'s imports.

---

## Priority 3 — Architectural friction (worth thinking about)

### [ ] Three names for one project

| Name | Where |
|---|---|
| `py-cad` | repo folder, README title, GitHub URL |
| `athor-sketches` | distribution name (`pyproject.toml:2`) |
| `py_cad` | actual import |

Whoever picks this up later (you, in 6 months) will lose time to it. Lowest-cost fix: rename `pyproject.toml` `name` to `py-cad`. That makes the distribution name match the repo name; the import name stays `py_cad` (PyPI convention: hyphens in distribution → underscores in import).

```toml
# pyproject.toml
name = "py-cad"  # was "athor-sketches"
```

After renaming, regenerate the lock: `uv lock`.

---

### [ ] `enum_helpers` is the most useful module for new users but isn't in the public API

`from py_cad import StrAutoEnum` works; `from py_cad import create_str_enum, extend_str_enum` doesn't. Users who want to dynamically build enums (the obvious power-user use case) have to know the internal layout (`from py_cad.enum_helpers import …`).

**Fix:** re-export the public functions:

```python
# src/py_cad/__init__.py
from .core import BasicDimensionData, DimensionData, BuilderABC, AssemblerABC
from .helpers import StrAutoEnum, NormalizedDict
from .enum_helpers import create_str_enum, extend_str_enum

__all__ = [
    "BasicDimensionData", "DimensionData", "BuilderABC", "AssemblerABC",
    "StrAutoEnum", "NormalizedDict",
    "create_str_enum", "extend_str_enum",
]
```

`NormalizedDict` is debatable but useful enough that exposing it costs little.

---

### [ ] The two `BoxDimensionData`s have the same name but different contracts

- `src/py_cad/primitives/basic_box/project_data.py:31` — real `DimensionData` subclass; `mat_thickness` is a **dict** mapping part types to thicknesses
- `src/py_cad/primitives/plywood_box/project_data.py:30` — `BoxDimensionData = DimensionData` (alias); expected `mat_thickness` as a **scalar**

Same type name, incompatible call shapes. Confusing if you import `BoxDimensionData` from one and accidentally use the other's API.

**Fix:** rename one. `PlywoodBoxDimensionData = DimensionData` is fine since plywood-box doesn't actually need a custom subclass. Or: drop the alias entirely from `plywood_box/project_data.py:30` and let users import `DimensionData` directly.

---

### [ ] `Part.TOP: PartType.BOTTOM` in plywood_box is uncommented

**Where:** `src/py_cad/primitives/plywood_box/project_data.py:26`

```python
PART_TYPE_MAP = {
    ...
    Part.TOP: PartType.BOTTOM,   # ← top reuses BOTTOM geometry
}
```

Probably intentional — the plywood box top is visually identical to the bottom — but a one-line comment would save the next reader a head-scratch.

---

### [ ] `projects/generic_plywood_box.py` is incomplete

```python
from py_cad.primitives.plywood_box.project_data import BoxDimensionData

BOX_X = 300
BOX_Y = 200
BOX_Z = 200
PLY_THICKNESS = 9
ROUTE_DEPTH = PLY_THICKNESS / 2

BOX_DIMENSIONS = BoxDimensionData(
    (BOX_X, BOX_Y, BOX_Z), mat_thickness=PLY_THICKNESS, route_depth=ROUTE_DEPTH
)
```

It only constructs `BOX_DIMENSIONS`. Compare to `projects/generic_box.py` which has `get_builder()`/`get_assembler()` helpers. Either:
- Add the same helpers, or
- Delete this file (it's used by `man_testing.py` only for `BOX_DIMENSIONS` import — that import would still work either way as long as the constants stay)

---

### [ ] `DimensionData` does double-duty (low-priority, mention only)

It holds global dimensions AND per-part-type sub-dimensions on the same object. For more complex projects this gets crowded; you might eventually want `ProjectDimensions` (global) holding a `PartDimensionsMap` (per-type). Cosmetic separation of concerns — only worth doing if you actually feel the friction.

---

## Priority 4 — Cleanup punchlist

### [ ] Fix `show_objects.py` mixed import paths

Lines 2-3 use the wrong style (`from projects.garbage_sort_box.…` — works only if run from the project root with `projects/` on `sys.path`); lines 13-15 use the correct package-relative style (`from py_cad.primitives.…`). Pick one consistently — the `py_cad.primitives.…` style is more robust.

Also, this file is meant to be loaded into CQ-editor — lines 79 (`show_object(assembly, name)`) only works in that context. Add a top-of-file comment saying so.

---

### [ ] Drop dead `top_divider_y/z` class attributes

**Where:** `src/py_cad/primitives/plywood_box/parts.py:7-8`, `projects/garbage_sort_box/parts.py:7-8`, `tests/test_project/parts.py:7-8`

```python
class Builder(BuilderABC):
    top_divider_y = 300   # never referenced
    top_divider_z = 300   # never referenced
```

Delete them. `top_divider_x` (set in `__init__`) is real.

---

### [ ] Add minimal CI

A 10-line GitHub Actions workflow running `uv sync && uv run python -m unittest discover tests` on push/PR. Cheap insurance, catches the kinds of regressions that the test suite is *already* designed to catch.

```yaml
# .github/workflows/test.yml
name: tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run python -m unittest discover tests
```

---

### [ ] Stray `# pylint: disable=…` comments without a pylint config

Search results across the codebase:
- `src/py_cad/primitives/basic_box/assembly.py:11,26`
- `src/py_cad/primitives/plywood_box/assembly.py:11,26`
- `projects/garbage_sort_box/assembly.py:11,23`
- `tests/test_dimension_data.py:12,13`
- `tests/test_project/assembly.py:32,50,67,84,104`
- `src/py_cad/core.py:335,432,442,500`

These come from your IDE flagging things pylint doesn't understand (decorators, dynamic attrs from `_PostInitMeta`). Two options:
- Add a `pyproject.toml` `[tool.pylint]` config with the right exclusions, or
- Strip them. They're noise without a configured linter.

If you want a linter at all, consider `ruff` instead — much faster, fewer false positives on metaclass-heavy code.

---

### [ ] Optional: add `pyright` or `mypy` config

Code is heavily type-hinted but nothing checks the hints. A `pyproject.toml` `[tool.pyright]` block (10 lines) would catch the kinds of errors annotations are designed to prevent.

---

## What I deliberately did NOT flag

- The `_PostInitMeta` metaclass approach — defensible; the alternative (calling `_post_init` manually in every `__init__`) is more error-prone for a framework users will subclass.
- `# pylint: disable=no-value-for-parameter` on `cq.Location(...)` calls — that's a known cadquery typing limitation, not your fault.
- The choice of `unittest` over `pytest` — works fine, no reason to migrate.
- The `cq.Color("burlywood")` default in `AssemblerABC.__init__` — minor wasted allocation, not worth a fix.
