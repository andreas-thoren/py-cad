# CLAUDE.md

Notes for Claude when working in this repo. Read first.

## What this is

A small parametric-CAD framework on top of [CadQuery](https://github.com/CadQuery/cadquery), built by Andreas (a hobbyist) to make woodworking sketches easier — boxes, cabinets, panels with grooves and routing. The framework is the interesting part; the woodworking projects (`projects/`, `src/py_cad/primitives/`) are sample consumers.

The author cares about clean abstractions and uses inheritance heavily — partial assemblers/builders compose into full ones via Python's MRO. Don't dismiss the "over-engineered for a hobby" feel: it's deliberate, and the test suite exercises it.

## Naming you'll encounter

Three names refer to the same project. This is messy but historical:

| Name | Where |
|---|---|
| `py-cad` | repo folder, README title, GitHub URL |
| `py-cad` | distribution name (`pyproject.toml` `name`) |
| `py_cad` | actual import (`from py_cad import ...`) |

When writing code or docs, use `py_cad` for imports and `py-cad` for project references. Don't try to "fix" this without asking — it would touch every import.

## Architecture (the mental model)

Four orthogonal axes that the user must wire together for a project:

1. **`Part`** — concrete instances in the assembly (e.g. `LONG_SIDE`, `LONG_SIDE_INVERSE`). Usually a `StrAutoEnum`.
2. **`PartType`** — geometry templates (e.g. `LONG_SIDE_PANEL`). Often fewer than `Part`s because mirrored/rotated parts share geometry.
3. **`DimensionData`** — global dimensions + per-part-type dimensions/attributes. Subclass to compute derived dims and implement `get_part_types_dimensions()`.
4. **`BuilderABC`** + **`AssemblerABC`** — geometry construction (`@BuilderABC.register(part_type)`) and assembly placement (`get_metadata_map()`).

Public API lives in `src/py_cad/__init__.py`: `BasicDimensionData`, `DimensionData`, `BuilderABC`, `AssemblerABC`, `StrAutoEnum`. Everything else is internal.

## Non-obvious framework mechanics

- **`_PostInitMeta`** (`helpers.py`) — metaclass that runs `_post_init(*args, **kwargs)` after `__init__`. `BasicDimensionData` and `DimensionData` use it to freeze attributes / resolve part-type dimensions. **Don't override `_post_init` in user subclasses** — it's framework internals.
- **`NormalizedDict`** (`helpers.py`) — case-insensitive, whitespace-stripped string keys. Used everywhere maps are keyed by part/part-type. `dict["FOO"]` and `dict[" foo "]` resolve to the same entry. Non-string keys are passed through unchanged on lookup, but rejected on set.
- **`InheritanceMixin.get_parent_items`** — walks the MRO to merge an attribute across parents. Younger (more derived) classes win on collision. Used by `BuilderABC._builder_map` and `AssemblerABC._resolved_part_map`. The variable named `older_parent_items` inside this method is misleading — in the first iteration it's actually the youngest parent.
- **`@BuilderABC.register(part_type)`** — decorator that tags a method; `__init_subclass__` then walks the class dict to populate `_builder_map`. Inheriting a builder gives you the parent's registered methods automatically.
- **Inheritance with diamond is supported** — see `tests/test_project/assembly.py` for `PartialAssemblerLeaf(PartialAssemblerMidOne, PartialAssemblerMidTwo)`. Each level can register its own `part_map` and `get_metadata_map`; framework merges them by MRO.
- **`AssemblerABC._setup_attributes`** — class attributes (`part_map`, `BuilderClass`) are deleted from the class after `__init_subclass__` resolves them. Don't try to read `self.part_map` on an instance; use `self.resolved_part_map` (property).

## Build / test / run

```bash
# Setup (uv installs project + dev tools, locks deps)
uv sync

# With CQ-editor GUI for visualization
uv sync --extra editor
uv run cq-editor

# Tests (uses unittest, NOT pytest)
uv run python -m unittest discover tests

# Lint + format (ruff handles both; replaces black)
uv run ruff check          # report issues
uv run ruff check --fix    # auto-fix safe issues
uv run ruff format         # apply formatting
```

`pyproject.toml` declares `required-environments` for both Linux x86_64 and Windows AMD64; the lockfile pins `pyqt5-qt5==5.15.2` because that's the last version with wheels on both. The author uses both OSes.

## Files to know

- `src/py_cad/core.py` — the four ABCs + `BasicDimensionData`/`DimensionData`. The whole framework is here.
- `src/py_cad/helpers.py` — `StrAutoEnum`, `NormalizedDict`, `InheritanceMixin`, `_PostInitMeta`.
- `src/py_cad/enum_helpers.py` — `create_str_enum`, `extend_str_enum`, etc. **Not** in `__init__.py`'s public API; users must `from py_cad.enum_helpers import ...`.
- `src/py_cad/primitives/{basic_box,plywood_box}/` — example builders/assemblers shipped with the package. Only `basic_box` defines its own `BoxDimensionData` subclass (per-part-type thickness dict); `plywood_box` uses the bare `DimensionData` directly with a scalar `mat_thickness`.
- `tests/test_project/` — fixtures used by `test_assembler.py` and `test_builder.py`. Multi-level inheritance (`Base → Mid → Leaf → OuterLeaf`) is the heart of the test suite.
- `projects/garbage_sort_box/` — real consumer project (woodworking).

## Repo-root scripts (handle with care)

- `man_testing.py` — minimal smoke-test launcher for the plywood box. Working as of last cleanup.
- `show_objects.py` — meant to be opened in CQ-editor (the `show_object()` call only resolves there). Has mixed import styles between functions; some use `from projects.…` (only works if run from repo root) and some use `from py_cad.primitives.…` (more robust). Functional but inconsistent — see `CODE_REVIEW.md` if cleaning up.

## Coding conventions

- `from __future__ import annotations` is **not** used; the project requires Python 3.10+ and uses real `|` unions in annotations directly.
- Docstrings are present on most public methods and are detailed. Match the style if adding code.
- Tests use `unittest`, not pytest. Keep that.
- Lint and format are handled by `ruff` (configured in `pyproject.toml` `[tool.ruff]`, line-length 100, rule families E/F/I). `show_objects.py` is fully excluded via `extend-exclude` because it relies on CQ-editor's runtime `show_object` and the script style isn't worth shaping.
- `cq.Workplane` is the build output; `cq.Assembly` is the assemble output; `cq.Color("burlywood")` is the default part color (set in `AssemblerABC.__init__`).

## Common pitfalls

- **Don't pass a string as `basic_dimensions`** — `set_basic_dimensions` checks `isinstance(..., Sequence) and len(...) == 3`, which a 3-char string passes. Validation gap.
- **`get_part_types_dimensions` return shape**: each value is either `(x, y, z)` or `((x, y, z), {extras})`. The runtime match in `DimensionData._normalize_part_type_dimensions` will raise `TypeError` for anything else.
- **Subclassing `BasicDimensionData`/`DimensionData`**: call `super().__init__(...)` early in your `__init__`. Attributes set before that call are allowed (freeze hasn't happened yet); attributes set after `_post_init` runs would fail.
- **`build_part(part_type)` calls `build_func(self)` with no extra args** — any extra parameters on a registered builder method (e.g. `invert_grooves=False` in `plywood_box/parts.py`) are dead. The framework provides no path to pass them. Either remove the parameter or extend `build_part` to forward kwargs.
