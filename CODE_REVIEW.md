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

### [x] `set_basic_dimensions` doesn't reject strings

**Resolution (2026-04-30):** Applied the proposed fix in `src/py_cad/core.py:76-83` — added `isinstance(basic_dimensions, str)` rejection and per-element `isinstance(d, (int, float))` validation. `BasicDimensionData("abc")` now raises `TypeError` instead of silently accepting `x_len="a"`. The 43-test suite still passes.

Edge case left unaddressed: `bytes`/`bytearray` of length 3 still pass (their elements are `int`). If that ever becomes a real concern, add `or isinstance(basic_dimensions, (bytes, bytearray))` to the check.

---

## Priority 2 — Misleading code (no incorrect behavior, but readers will trip)

### [x] Dead test assertion in `test_dimension_data.py:18`

**Resolution (2026-04-30):** Changed `self.new_attribute = 42` → `data.new_attribute = 42`. The line now correctly demonstrates that adding a *new* attribute after freeze is allowed (the implicit assertion is "doesn't raise"), complementing the existing assertion below that modifying an *existing* attribute raises. Verified by re-reading `BasicDimensionData.__setattr__`: the freeze check only fires when `name in self.__dict__`, so genuinely new attributes pass through.

---

### [x] `older_parent_items` is misnamed in `helpers.py:71-82`

**Resolution (2026-04-30):** Renamed `older_parent_items` → `current_items` in `InheritanceMixin.get_parent_items`. Pairs naturally with the loop iteration, stays generic over `set`/`dict` (preserves the type hint), and drops the misleading age implication. Also rewrote the inline comment to clarify the merge direction (`parent_items` accumulates younger-precedent entries; merging older `current_items` on the left lets younger win on collision).

---

### [x] `AssemblerABC` docstring numbers requirements 1, 3, 4 (skips 2)

**Resolution (2026-04-30):** Fixed by user. Now numbered 1, 2, 3 in `src/py_cad/core.py:350-354`.

---

### [x] `tests/test_normalized_dict.py:2` imports from wrong module

**Resolution (2026-04-30):** Fixed by user. Now imports `from py_cad.helpers import NormalizedDict` directly.

---

## Priority 3 — Architectural friction (worth thinking about)

### [x] Three names for one project

**Resolution (2026-04-30):** Fixed by user. Distribution renamed `athor-sketches` → `py-cad` in `pyproject.toml:2`; lockfile regenerated. Now consistent: distribution `py-cad`, repo `py-cad`, import `py_cad` (the underscore form is the standard hyphen → underscore PyPI convention).

---

### [x] `enum_helpers` is the most useful module for new users but isn't in the public API

**Resolution (2026-04-30):** `src/py_cad/__init__.py` now re-exports `NormalizedDict` (from `helpers`) and `create_str_enum`/`extend_str_enum` (from `enum_helpers`). All available as `from py_cad import …`. Verified by smoke test.

---

### [x] The two `BoxDimensionData`s have the same name but different contracts

**Resolution (2026-04-30):** Picked **drop the alias** — `BoxDimensionData = DimensionData` removed from `plywood_box/project_data.py`. Only consumer (`projects/generic_plywood_box.py`) updated to import `DimensionData` directly. If plywood-box later needs per-panel thickness logic, add a real subclass then. Naming collision is gone — only `basic_box` ships a `BoxDimensionData` now.

---

### [x] `Part.TOP: PartType.BOTTOM` in plywood_box is uncommented

**Resolution (2026-04-30):** Added inline comment in `plywood_box/project_data.py` above the `Part.TOP` mapping: "Top reuses BOTTOM geometry — for this style the panels are visually identical."

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
