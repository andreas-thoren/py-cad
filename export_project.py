"""Smoke test for py_cad.export against the ``generic_box`` sample project.

Run from the repo root:

    uv run python export_project.py

Demonstrates the recommended workflow: build a single ``Builder`` and
share it between :func:`py_cad.export.export_part_types` and the
``Assembler`` (via the new ``builder=`` kwarg on ``AssemblerABC``), so the
geometry isn't built twice.

Outputs land under ``out/generic_box/``:

    bottom.step
    long_side_panel.step
    short_side_panel.step
    top.step
    assembly.step

Open any of these in CQ-editor or FreeCAD to verify the geometry
round-trips cleanly.
"""

from pathlib import Path

from projects.generic_box import BOX_DIMENSIONS, get_builder
from py_cad import export_assembly, export_part_types
from py_cad.primitives.basic_box import Assembler

OUT = Path("out/generic_box")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # Build one Builder up front. Both exports share it.
    builder = get_builder()

    part_paths = export_part_types(builder, OUT, file_format=".svg")
    print(f"Wrote {len(part_paths)} part files in {OUT}/")
    for path in part_paths:
        print(f"  {path.name} ({path.stat().st_size:,} bytes)")

    # Pass the same Builder to the Assembler via the new builder= kwarg.
    # Skips the duplicate Builder construction that AssemblerABC.__init__
    # would otherwise do on its own.
    assembler = Assembler(BOX_DIMENSIONS, builder=builder)

    assembly_path = export_assembly(assembler, OUT / "assembly.svg", file_format=".svg")
    print(f"Wrote {assembly_path.name} ({assembly_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
