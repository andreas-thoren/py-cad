# Export Implementation Plan

Plan for adding automatic drawing export to `py-cad`. The goal is to replace
the previous manual workflow (export to FreeCAD, annotate by hand) with
generated artifacts that carry their own dimensions and remain editable in
FreeCAD if postprocessing is needed.

---

## Goal & validated approach

Two outputs per project, regenerated from `py-cad` every time:

1. **Per-PartType DXF drawings** — one shop drawing per unique geometric
   template, showing one face of the part with overall L × W and a thickness
   note.
2. **Project overview** — a single isometric DXF of the assembly with overall
   L / W / H of the bounding box, plus a STEP file of the 3D assembly for
   visual reference / heavy postprocessing.

Number of drawings is bounded by the count of `PartType`s, not `Part`s.
Mirrored / rotated parts share a `PartType` and a single drawing.

### What we already validated (FreeCAD round-trip)

- `ezdxf` writes DXFs that FreeCAD imports as editable Draft `Dimension`,
  `Text`, and `Polyline` objects — no need for the legacy Python importer,
  only the **"Texter och måttsättningar"** preference flag.
- Standard 30°/30° isometric projection preserves edge length along the three
  principal axes, so aligned dims on an iso wireframe report correct true
  3D values without any scaling tricks.
- Setting `doc.units = ezdxf.units.MM` makes FreeCAD interpret values as mm.

---

## Phase 1 — Per-PartType shop drawings (detailed)

### Scope

In:
- One DXF per `PartType` discovered in `dim_data.part_types_dimensions`.
- Default behaviour only: outline of the largest face + L dim + W dim +
  thickness note + part-type label. No user-facing override surface yet.
- Hard requirement: project must use a `DimensionData` subclass with
  `get_part_types_dimensions()` populated.

Out:
- Project overview drawing (Phase 2).
- Override mechanism for extra dims / extra views (Phase 3).
- Exploded views (Phase 4).
- STEP export — already trivial via `cq.exporters.export(assy, ...)`; we'll
  add a thin convenience wrapper but not invent anything.

### Module layout

```
src/py_cad/export/
    __init__.py        # re-exports the public entry points
    dxf.py             # Phase 1 lives here
    step.py            # thin wrapper around cq.exporters.export
    geometry.py        # face-picking + 2D projection helpers (shared by phases)
```

`__init__.py` exposes:

```python
from py_cad.export import export_part_drawings, export_assembly_step
```

These are also re-exported from `py_cad/__init__.py` so the public API is
`from py_cad import export_part_drawings`.

### Public API

```python
def export_part_drawings(
    builder: BuilderABC,
    out_dir: str | Path,
) -> list[Path]:
    """Emit one DXF per PartType registered on builder, into out_dir.

    Iterates builder.dim.part_types_dimensions, builds each part, projects
    its largest face to 2D, and writes <out_dir>/<part_type>.dxf.
    Returns the list of written paths.
    """

def export_assembly_step(
    assembler: AssemblerABC,
    out_path: str | Path,
) -> Path:
    """Build the assembly and write it as a single STEP file."""
```

We accept a `BuilderABC` rather than an `AssemblerABC` for `export_part_drawings`
because per-PartType drawings have nothing to do with assembly placement —
the builder is already the right level of abstraction. Users with an
assembler in hand can just pass `assembler.builder`.

### Implementation steps

1. **Iterate PartTypes via the builder.**
   ```python
   for part_type in builder.part_types:
       solid = builder.build_part(part_type, cached_solid=True)
   ```
   `cached_solid=True` returns a `cq.Solid` (avoids rebuilding when called
   multiple times from the same builder).

2. **Pick the drawing face.**
   - Enumerate `solid.Faces()`.
   - Filter to planar faces (skip cylinders / curves; woodworking parts are
     overwhelmingly planar).
   - Pick the one with the largest area.
   - If tied, prefer the one whose normal aligns with the +Z direction (gives
     us a stable choice across runs).
   - **Defensive warning**: if the second-largest planar face has area
     within 1.5× of the chosen face, log a warning. This signals the
     heuristic is on shaky ground and the user likely needs a Phase 3
     override to pick the correct face explicitly.

3. **Project face edges to 2D.**
   - From the chosen face, get its outer wire and any inner wires (for
     parts with through-holes, though Phase 1 woodworking parts shouldn't
     hit this).
   - Build a local 2D coordinate frame from the face: origin at face center,
     X axis aligned with the **longest straight edge of the face's outer
     wire** (anchors the drawing to a real geometric feature and avoids
     coordinate-frame ambiguity from a world-aligned face bounding box),
     Y axis perpendicular within the face plane.
     **Fallback** for the rare case of a fully-curved outer wire (round
     panels, cylindrical parts): align local X to the world X axis
     instead so the projection step doesn't crash.
   - **Classify each edge by geometric type** via CadQuery's
     `Edge.geomType()` and emit the appropriate primitive in step 5:
     straight edges contribute to polyline segments; arcs and full circles
     are preserved as native DXF `ARC` / `CIRCLE` entities (so FreeCAD can
     still snap to centers during postprocessing — tessellated curves
     can't); splines or other freeform curves tessellate at a tolerance
     (e.g. 0.5 mm chord deviation) as a last-resort fallback.
   - Project each edge's defining points (endpoints for straight; center +
     radius + angles for arcs/circles) to the local (u, v) frame.
   - Translate the 2D outline so its bbox sits in the positive quadrant
     with a small margin from origin.

4. **Compute draw-time dimensions.**
   - L = bbox extent along local X, W = extent along local Y, T = solid's
     bounding-box extent along the face normal.
   - **Sanity-check** against `dim_data[part_type].x_len/y_len/z_len` and
     log a warning if they diverge. For Phase 1 axis-aligned panels they
     should match exactly — any mismatch is a canary that the face-pick
     heuristic landed on the wrong face, not a precision problem to
     paper over.
   - Use these **geometric** values for both placement and display.
     **Do not** override DIMENSION entity text with the `DimensionData`
     value (breaks the FreeCAD parametric link — see the "display
     precision and parametric editability" bullet under Open Questions).
     `$DIMDEC` controls dim display precision globally; the thickness
     TEXT note uses `f"{T:.1f}"` for its own rounding (it's a static
     annotation, not a DIMENSION, so the parametric concern doesn't
     apply there).

5. **Emit the DXF via `ezdxf`.**
   - `doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM`
   - Outline: emit each edge as the appropriate `ezdxf` primitive —
     straight runs as `msp.add_lwpolyline([(u, v), ...], close=True)`,
     arcs as `msp.add_arc(center, radius, start_angle, end_angle)`, full
     circles as `msp.add_circle(center, radius)`. For Phase 1 woodworking
     panels the outer wire is fully straight and reduces to a single
     closed `LWPOLYLINE`; the dispatch matters once Phase 3 brings in
     parts with rounded features.
   - Compute the 2D bbox of the projected outline: `(u_min, v_min)` to
     `(u_max, v_max)`. **Dim lines are placed outside this bbox**, never at
     fractional positions that assume a rectangular silhouette — this keeps
     dims clear of L-shaped or cut-out parts.
   - L dim: `msp.add_linear_dim(base=((u_min+u_max)/2, v_min - margin), p1=(u_min, v_min), p2=(u_max, v_min), angle=0).render()`
   - W dim: `msp.add_linear_dim(base=(u_max + margin, (v_min+v_max)/2), p1=(u_max, v_min), p2=(u_max, v_max), angle=90).render()`
   - Thickness note: `msp.add_text(f"Thickness: {T:.1f} mm", dxfattribs={"height": 12}).set_placement((u_min, v_max + margin))`
   - Title text: part-type name placed above the outline.
   - `margin` scales with the larger of `(u_max - u_min)` / `(v_max - v_min)` (e.g. 8% of max dimension).

6. **Filename convention.**
   ```python
   safe_name = NormalizedDict.normalize_item(str(part_type))  # e.g. "long_side_panel"
   path = Path(out_dir) / f"{safe_name}.dxf"
   ```

### Default behaviour summary

| Element | Default | Source of truth |
|---|---|---|
| Face shown | Largest planar face | Geometry |
| L value | bbox extent along chosen face's local X | Geometry |
| W value | bbox extent along chosen face's local Y | Geometry |
| T value | bbox extent along face normal | Geometry |
| L dim placement | Below outline, centered | Auto |
| W dim placement | Right of outline, centered | Auto |
| Thickness | Text note above outline | Auto |
| Title | PartType name above outline | Auto |
| Filename | `{part_type_normalized}.dxf` | PartType |
| Units | mm (`$INSUNITS = 4`) | Hardcoded |

### Dependencies

- Add `ezdxf >= 1.4` to `pyproject.toml`.
- Place under a new optional group `[drawings]`:
  ```toml
  [project.optional-dependencies]
  editor = ["cq-editor>=0.7"]
  drawings = ["ezdxf>=1.4"]
  ```
- Import lazily inside `export/dxf.py` so users without the extra get a
  clear `ImportError` only when they actually call the export.

### Tests

- **Unit tests** (`tests/test_export_dxf.py`):
  - Run `export_part_drawings` against the existing `tests/test_project/`
    fixture (which already has a Builder + DimensionData subclass).
  - Parse the resulting DXF back with `ezdxf` and assert:
    - At least one `LWPOLYLINE` per file.
    - At least 2 `DIMENSION` entities per file.
    - Dimension values match expected L and W for that PartType.
    - Header `$INSUNITS == 4`.
- **Manual smoke test**: run against `projects/garbage_sort_box`, open the
  produced DXFs in FreeCAD, confirm Draft `Dimension` objects appear and
  read the right values.

### Acceptance criteria

- `uv run python -m unittest discover tests` passes (including new tests).
- `from py_cad import export_part_drawings; export_part_drawings(builder, "out")`
  produces N DXFs, where N == number of PartTypes in the project.
- All produced files open cleanly in FreeCAD with dimensions importable as
  Draft `Dimension` objects.
- Lint clean: `uv run ruff check && uv run ruff format --check`.

### Open questions to resolve while implementing

- Title-block conventions: just the PartType name, or also project name +
  date? (Default: PartType + project name from a passable kwarg, no date.)
- What to do when `get_part_types_dimensions` returns extras unrelated to
  drawing (e.g. `mat_thickness`)? They should just be ignored in Phase 1.
- Display precision and parametric editability — **DIMENSION entities
  must NOT receive a hardcoded `text=` override**: it breaks the
  parametric link in FreeCAD (if the user stretches the part, the dim
  line follows the new endpoints but the hardcoded text stays at the old
  value, silently misleading). Instead, set DXF header `$DIMDEC` (decimal
  places, e.g. 1) globally to control display precision and hide sub-mm
  noise. Thickness is rendered as a plain TEXT entity (not a DIMENSION),
  so it can safely use the design value directly with rounding
  (`f"{T:.1f}"`) — it's static either way. Float fuzz between the
  geometric bbox and design value is unlikely on axis-aligned Phase 1
  targets; if it surfaces later (e.g. rotated parts), snap geometry
  vertices to design values during the projection step rather than
  override the displayed dim text.

---

## Phase 2 — Project overview drawing (sketch)

Single DXF showing the assembly as an isometric wireframe with overall
L / W / H aligned dimensions, exactly like the validated `validate_overview.dxf`
prototype but driven by a real `Assembly`.

Approach:
- Take an `AssemblerABC`, build the assembly, get the overall bounding box.
- Draw the 9 visible edges of that bounding box in iso projection.
- Add three aligned dims along three principal-axis edges (overall L/W/H).
- Optional: also draw the iso silhouette of each part inside the bbox.
  Not needed for the v1 overview, but a low-effort upgrade.

Public API:
```python
def export_assembly_overview(assembler: AssemblerABC, out_path: str | Path) -> Path: ...
```

Reuses `geometry.py` for the iso projection helper.

Open question: do we want a 3-view (top/front/side) variant as an alternative
to iso? Decide after Phase 1; iso is the assumed default.

---

## Phase 3 — Override mechanism (sketch)

Drawing overrides are config data, not behavior — they belong with the rest
of the per-PartType metadata that `get_part_types_dimensions` already
returns. A `DrawingSpec` dataclass keeps the schema typed and discoverable
while avoiding a new ABC and a new method:

```python
from py_cad import DrawingSpec, ExtraDim

class BoxDimensionData(DimensionData):
    def get_part_types_dimensions(self):
        return {
            PartType.LONG_SIDE_PANEL: ((x, y, z), {
                "mat_thickness": 12,
                "drawing": DrawingSpec(
                    extra_dims=[ExtraDim("groove_offset", value=50, axis="u")],
                    extra_views=["edge"],
                ),
            }),
        }
```

`DrawingSpec` has two fields:
- `extra_dims: list[ExtraDim]` — additional dimension annotations beyond the
  default L/W/T. Each `ExtraDim` declares a name, value, axis (`u`/`v` in
  the drawing frame), and placement offset. **Future**: `ExtraDim` should
  grow a `kind` field with `"linear"` (default), `"diameter"`, `"radius"`
  variants once any project has rounded features — Phase 1 targets are all
  rectangular so linear is the only kind needed initially.
- `extra_views: list[str]` — additional faces to render. Default is the
  largest face only; overrides can request `"edge"`, `"top"`, etc. The
  Phase 1 face picker is reused for each requested view.

Defaults from Phase 1 apply whenever no `"drawing"` key is present in the
extras dict.

**Inheritance behavior**: unlike `get_metadata_map` (which the framework
walks across MRO via `_get_resolved_metadata_map`), `get_part_types_dimensions`
is called only once on the most-derived class. Inheritance is therefore
entirely user-driven: a subclass that wants to extend rather than replace
the parent's drawing specs calls `super().get_part_types_dimensions()` and
modifies the result. To make that ergonomic without inventing a framework-
wide deep-merge utility, give `DrawingSpec` small `with_*` builder methods:

```python
spec = parent_spec.with_extra_view("edge").with_extra_dim(ExtraDim(...))
```

These are one-liners using `dataclasses.replace` + list concatenation under
the hood. A recursive deep-merge utility is **deliberately not added** — it
would diverge from how `get_part_types_dimensions` already handles
inheritance and add framework complexity for a problem that's already
solvable with three lines of dataclass code per `with_*`.

(Considered an alternative `@DrawingABC.register` decorator parallel to
`BuilderABC.register` and rejected: drawing overrides are pure config, not
behavior, so a class+method scaffold would be heavy-handed for the
common case of "add one extra dim line.")

---

## Phase 4 — Exploded views (deferred, may not ship)

Hard problem: CadQuery has no native exploded-view facility. Would require:

- Per-Part "explode vectors" declaring which direction each part moves
  outward from the assembled position. Likely lives in `get_metadata_map`
  metadata or a new `get_explode_map`.
- An iso projection of the assembly with each part offset along its vector.
- Annotation of overall dims of the *original* (non-exploded) bounding box.

Defer until Phase 1+2 are in real use and we know whether the Phase 2
non-exploded iso overview is readable enough on real projects. If it is,
Phase 4 may never be needed.

---

## Composite projects (deferred)

Some projects are aggregates of smaller subprojects, each with its own
`Builder` / `Assembler` / `DimensionData` (e.g. a storage cabinet that
contains several identical drawers, where the drawer is itself a complete
project).

**Recommended construction pattern**: a sub-assembly is *not* a `PartType`
of the parent. Don't wrap it in a parent `BuilderABC` method that
flattens it to a single solid — flattening loses introspection (per-part
export, color separation, BOM, anything that walks the assembly tree).
Instead, override the parent `Assembler.assemble()` to nest the child
assembly via CadQuery's native `assy.add(sub_assy, loc=...)`:

```python
class FurnitureAssembler(AssemblerABC):
    BuilderClass = FurnitureBuilder  # furniture's own parts only

    def assemble(self, parts=None):
        assy = super().assemble(parts)
        for i, loc in enumerate(self.dim.drawer_locations):
            drawer = DrawerAssembler(self.dim.drawer_dim).assemble()
            assy.add(drawer, name=f"drawer_{i}", loc=loc)
        return assy
```

The drawer keeps its tree structure; the parent owns drawer placement
only. No framework changes required — the existing `cq.Assembly` already
supports this.

**Export behavior in the meantime (Phase 1+2 onward)**: composite
projects work by running the exporter once per project —
`export_part_drawings(drawer_builder, "out/drawer/")` and
`export_part_drawings(furniture_builder, "out/furniture/")` as two
separate calls. The Phase 2 overview drawing of the parent will include
drawer silhouettes via CadQuery's nested-assembly geometry, no special
handling needed at the projection step.

**Phase 4+ extension (optional convenience)**: a `Project` registry that
owns its sub-projects could expose a single `export_project(project)`
entry point that fans out to all sub-projects automatically and
aggregates output into one directory tree. Strictly a convenience layer
over what's already callable manually; deferred until composite projects
actually exist in `projects/` and the manual two-call workflow proves
annoying.

---

## Note: plywood_box refactor

`src/py_cad/primitives/plywood_box/project_data.py` currently uses bare
`DimensionData((BOX_X, BOX_Y, BOX_Z), mat_thickness=PLY_THICKNESS)` with no
subclass and no `get_part_types_dimensions`. Under Phase 1 it would have an
empty `part_types_dimensions` map and produce zero DXFs.

When time allows, refactor to a `PlywoodBoxDimensionData` subclass with a
real `get_part_types_dimensions` populating the three PartTypes
(`BOTTOM`, `LONG_SIDE_PANEL`, `SHORT_SIDE_PANEL`). The geometry is simple —
all three are flat plywood panels with thickness `mat_thickness`, sized
from the project-wide `x_len`, `y_len`, `z_len`. Pattern to follow is
`primitives/basic_box/project_data.py:BoxDimensionData`.

This refactor is independent of Phase 1 and should not block it.
`basic_box` and `garbage_sort_box` already have proper subclasses and can
serve as the development / smoke-test targets.
