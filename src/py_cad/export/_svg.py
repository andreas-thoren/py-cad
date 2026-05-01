"""SVG-format writers used by ``py_cad.export``.

CadQuery's SVG exporter only operates on Workplane / Shape objects, not
on ``cq.Assembly``. ``write_assembly`` therefore flattens the assembly
into a single ``Compound`` first and exports that. Per-part colors set
in ``get_metadata_map`` are lost in the flattening — every line is drawn
in the default stroke colour. That is fine for a printed shop sketch
where colours wouldn't survive the printer anyway.

Default options are tuned for a printable workshop sketch:

- ``showAxes=False`` — keep the page clean.
- ``showHidden=True`` — grooves and dado pockets show through, which is
  exactly what a woodworker needs to mark out cuts.
- ``strokeWidth=0.5`` — readable at A4/Letter print size; CadQuery's
  default of 0.25 is too thin.

Other options (projection direction, dimensions, hidden-line colour) are
left at CadQuery's defaults for now; revisit once real prints expose
something that needs tweaking.
"""

from pathlib import Path

import cadquery as cq

_DEFAULT_OPTS: dict = {
    "showAxes": False,
    "showHidden": True,
    "strokeWidth": 0.5,
}


def write_part(workplane: cq.Workplane, path: Path) -> None:
    """Write a single part Workplane to ``path`` as SVG."""
    workplane.export(str(path), opt=_DEFAULT_OPTS)


def write_assembly(assembly: cq.Assembly, path: Path) -> None:
    """Write a CadQuery Assembly to ``path`` as SVG.

    Assembly is flattened to a single ``Compound`` first because SVG
    export operates on shapes. Per-part colours are lost in the flatten.
    """
    compound = assembly.toCompound()
    compound.export(str(path), opt=_DEFAULT_OPTS)
