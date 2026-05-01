"""Export entry points for py-cad models.

Two utility functions:

* ``export_part_types`` — emit one file per registered ``PartType`` of a
  ``BuilderABC`` instance into a directory.
* ``export_assembly`` — emit one file for an assembled model from an
  ``AssemblerABC`` instance.

Phase 1 supports only STEP. The format dispatch below routes the
file_format to a private sibling module (``_step``); future formats
(PDF, SVG, ...) add their own ``_<name>.py`` and an entry in
``_FORMAT_HANDLERS``.
"""

from collections.abc import Iterable
from pathlib import Path
from types import ModuleType

from ..core import AssemblerABC, BuilderABC
from ..helpers import NormalizedDict
from . import _step

__all__ = ["export_part_types", "export_assembly"]

# File extension → handler module. Each handler module exposes
# ``write_part(workplane, path)`` and ``write_assembly(assembly, path)``.
_FORMAT_HANDLERS: dict[str, ModuleType] = {
    ".step": _step,
}


def export_part_types(
    builder: BuilderABC,
    out_dir: str | Path,
    part_types: Iterable[str] | None = None,
    file_format: str = ".step",
) -> list[Path]:
    """Emit one file per PartType into ``out_dir``.

    Args:
        builder: Concrete ``BuilderABC`` instance whose registered
            PartTypes drive the export.
        out_dir: Directory to write files into. Created if missing.
        part_types: Iterable of PartTypes to export. ``None`` (default)
            means every PartType registered on ``builder``. Each entry
            must be in ``builder.part_types``; otherwise a ``ValueError``
            is raised listing valid PartTypes.
        file_format: Output format. Phase 1 supports only ``".step"``.
            Case-insensitive; the leading dot is optional.

    Returns:
        List of paths written, in the order PartTypes were processed.
    """
    fmt, handler = _resolve_format(file_format)

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    if part_types is None:
        target_part_types: list[str] = list(builder.part_types)
    else:
        target_part_types = list(part_types)
        _validate_membership(target_part_types, builder.part_types, label="PartType")

    written: list[Path] = []
    for part_type in target_part_types:
        wp = builder.build_part(part_type)
        safe_name = NormalizedDict.normalize_item(str(part_type))
        path = out_path / f"{safe_name}{fmt}"
        handler.write_part(wp, path)
        written.append(path)
    return written


def export_assembly(
    assembler: AssemblerABC,
    out_file_path: str | Path,
    parts: Iterable[str] | None = None,
    file_format: str = ".step",
) -> Path:
    """Emit a single file for the assembled model at ``out_file_path``.

    Args:
        assembler: Concrete ``AssemblerABC`` instance.
        out_file_path: File path to write to. Parent directory is
            created if missing. If the path has no suffix, the
            ``file_format`` extension is appended; if it has a suffix it
            must match ``file_format`` (case-insensitive), otherwise a
            ``ValueError`` is raised.
        parts: Iterable of Parts to include in the assembly. ``None``
            (default) builds the assembler's full part_map. Each entry
            must be in ``assembler.resolved_part_map``; otherwise a
            ``ValueError`` is raised listing valid Parts.
        file_format: Output format. Phase 1 supports only ``".step"``.

    Returns:
        The path written to (with any defaulted extension applied).
    """
    fmt, handler = _resolve_format(file_format)

    path = Path(out_file_path)
    if path.suffix == "":
        path = path.with_suffix(fmt)
    elif path.suffix.lower() != fmt:
        raise ValueError(
            f"out_file_path suffix {path.suffix!r} does not match file_format {fmt!r}."
        )
    path.parent.mkdir(parents=True, exist_ok=True)

    if parts is not None:
        parts = list(parts)
        _validate_membership(parts, assembler.resolved_part_map.keys(), label="Part")

    assembly = assembler.assemble(parts)
    handler.write_assembly(assembly, path)
    return path


# --- Internal helpers --------------------------------------------------------


def _resolve_format(file_format: str) -> tuple[str, ModuleType]:
    """Resolve ``file_format`` (with or without leading dot, any case) to
    its canonical lower-case ``.ext`` and the handler module that writes
    that format. Raises ``ValueError`` for unsupported formats."""
    fmt = file_format.lower()
    if not fmt.startswith("."):
        fmt = "." + fmt
    if fmt not in _FORMAT_HANDLERS:
        raise ValueError(
            f"Unsupported file_format {file_format!r}. Supported: {sorted(_FORMAT_HANDLERS)}"
        )
    return fmt, _FORMAT_HANDLERS[fmt]


def _validate_membership(requested: Iterable[str], allowed: Iterable[str], label: str) -> None:
    """Raise ``ValueError`` if any item in ``requested`` is not in
    ``allowed``. ``label`` is used in the error message (e.g. ``"PartType"``,
    ``"Part"``). Comparison normalizes via ``NormalizedDict.normalize_item``
    to match the framework's case/whitespace handling."""
    allowed_set = {NormalizedDict.normalize_item(a) for a in allowed}
    invalid = [r for r in requested if NormalizedDict.normalize_item(r) not in allowed_set]
    if invalid:
        raise ValueError(f"Invalid {label}(s): {invalid}.\nValid: {sorted(allowed_set)}")
