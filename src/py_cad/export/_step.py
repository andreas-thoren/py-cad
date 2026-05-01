"""STEP-format writers used by ``py_cad.export``.

Other format helpers live in sibling private modules (``_pdf.py``,
``_svg.py``, etc.). The public dispatch in ``export/__init__.py`` looks
up the right module by file extension and calls these two functions.
"""

from pathlib import Path

import cadquery as cq


def write_part(workplane: cq.Workplane, path: Path) -> None:
    """Write a single part Workplane to ``path`` as STEP."""
    workplane.export(str(path))


def write_assembly(assembly: cq.Assembly, path: Path) -> None:
    """Write a CadQuery Assembly to ``path`` as STEP."""
    assembly.export(str(path))
