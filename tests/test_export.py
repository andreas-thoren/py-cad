"""Tests for ``py_cad.export.export_part_types`` and ``export_assembly``.

Covers STEP (default) and SVG output, plus format dispatch behavior.
Tests use the existing ``tests/test_project`` fixture (subclassed
DimensionData with a fully registered builder + assembler) and a
temporary directory per test.
"""

import tempfile
import unittest
from pathlib import Path

from py_cad import export_assembly, export_part_types
from tests.test_project.assembly import PartialAssemblerOuterLeaf
from tests.test_project.parts import PartialBuilderOuterLeaf
from tests.test_project.project_data import DIMENSION_DATA, Part, PartType

STEP_HEADER_PREFIX = "ISO-10303-21"


def _read_first_line(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()[0]


class TestExportPartTypes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = PartialBuilderOuterLeaf(DIMENSION_DATA)

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_default_writes_one_step_per_registered_part_type(self):
        paths = export_part_types(self.builder, self.tmp_dir)
        self.assertEqual(len(paths), len(self.builder.part_types))
        for path in paths:
            self.assertTrue(path.exists())
            self.assertEqual(path.suffix, ".step")
            self.assertGreater(path.stat().st_size, 0)
            self.assertTrue(_read_first_line(path).startswith(STEP_HEADER_PREFIX))

    def test_filenames_match_normalized_part_type(self):
        paths = export_part_types(self.builder, self.tmp_dir)
        names = {p.stem for p in paths}
        expected = {pt.value for pt in PartType}
        self.assertEqual(names, expected)

    def test_subset_emits_only_requested_part_types(self):
        paths = export_part_types(self.builder, self.tmp_dir, part_types=[PartType.BOTTOM])
        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0].name, "bottom.step")

    def test_unknown_part_type_raises(self):
        with self.assertRaises(ValueError) as ctx:
            export_part_types(self.builder, self.tmp_dir, part_types=["not_a_real_pt"])
        self.assertIn("not_a_real_pt", str(ctx.exception))

    def test_creates_out_dir_if_missing(self):
        nested = self.tmp_dir / "deep" / "nested" / "dir"
        paths = export_part_types(self.builder, nested, part_types=[PartType.BOTTOM])
        self.assertTrue(nested.exists())
        self.assertEqual(len(paths), 1)


class TestExportAssembly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assembler = PartialAssemblerOuterLeaf(DIMENSION_DATA)

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_default_writes_single_step_file(self):
        path = export_assembly(self.assembler, self.tmp_dir / "assy.step")
        self.assertTrue(path.exists())
        self.assertEqual(path.suffix, ".step")
        self.assertGreater(path.stat().st_size, 0)
        self.assertTrue(_read_first_line(path).startswith(STEP_HEADER_PREFIX))

    def test_subset_of_parts_still_produces_valid_step(self):
        path = export_assembly(self.assembler, self.tmp_dir / "subset.step", parts=[Part.BOTTOM])
        self.assertTrue(path.exists())
        self.assertTrue(_read_first_line(path).startswith(STEP_HEADER_PREFIX))

    def test_unknown_part_raises(self):
        with self.assertRaises(ValueError) as ctx:
            export_assembly(
                self.assembler,
                self.tmp_dir / "broken.step",
                parts=["not_a_real_part"],
            )
        self.assertIn("not_a_real_part", str(ctx.exception))

    def test_appends_default_suffix_when_missing(self):
        path = export_assembly(self.assembler, self.tmp_dir / "no_extension")
        self.assertEqual(path.suffix, ".step")
        self.assertTrue(path.exists())

    def test_extension_mismatch_raises(self):
        with self.assertRaises(ValueError):
            export_assembly(
                self.assembler,
                self.tmp_dir / "wrong.svg",
                file_format=".step",
            )

    def test_creates_parent_dir_if_missing(self):
        nested = self.tmp_dir / "deep" / "nested" / "assy.step"
        path = export_assembly(self.assembler, nested)
        self.assertTrue(path.exists())


class TestFormatDispatch(unittest.TestCase):
    """Format-string normalization and unsupported-format errors apply
    to both export functions; cover them once each."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmp.name)
        self.builder = PartialBuilderOuterLeaf(DIMENSION_DATA)
        self.assembler = PartialAssemblerOuterLeaf(DIMENSION_DATA)

    def tearDown(self):
        self._tmp.cleanup()

    def test_unsupported_format_raises_for_part_types(self):
        with self.assertRaises(ValueError) as ctx:
            export_part_types(self.builder, self.tmp_dir, file_format=".dxf")
        self.assertIn(".dxf", str(ctx.exception))

    def test_unsupported_format_raises_for_assembly(self):
        with self.assertRaises(ValueError) as ctx:
            export_assembly(
                self.assembler,
                self.tmp_dir / "assy.step",
                file_format=".dxf",
            )
        self.assertIn(".dxf", str(ctx.exception))

    def test_format_string_accepts_no_dot_and_uppercase(self):
        # All four spellings should resolve to .step.
        for fmt in ("step", ".step", "STEP", ".STEP"):
            with self.subTest(fmt=fmt):
                paths = export_part_types(
                    self.builder,
                    self.tmp_dir,
                    part_types=[PartType.BOTTOM],
                    file_format=fmt,
                )
                self.assertEqual(paths[0].suffix, ".step")


class TestSvgFormat(unittest.TestCase):
    """Phase 2 SVG output. Verifies that ``file_format=".svg"`` produces
    valid SVG files from both export entry points. SVG is a paper-friendly
    format intended for workshop printouts."""

    @classmethod
    def setUpClass(cls):
        cls.builder = PartialBuilderOuterLeaf(DIMENSION_DATA)
        cls.assembler = PartialAssemblerOuterLeaf(DIMENSION_DATA)

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    @staticmethod
    def _looks_like_svg(path: Path) -> bool:
        text = path.read_text(encoding="utf-8", errors="replace")
        head = text.splitlines()[0]
        return head.startswith("<?xml") and "<svg" in text

    def test_part_types_emits_one_svg_per_part_type(self):
        paths = export_part_types(self.builder, self.tmp_dir, file_format=".svg")
        self.assertEqual(len(paths), len(self.builder.part_types))
        for path in paths:
            with self.subTest(path=path.name):
                self.assertEqual(path.suffix, ".svg")
                self.assertTrue(path.exists())
                self.assertTrue(self._looks_like_svg(path))

    def test_assembly_emits_single_svg(self):
        path = export_assembly(self.assembler, self.tmp_dir / "assy.svg", file_format=".svg")
        self.assertEqual(path.suffix, ".svg")
        self.assertTrue(self._looks_like_svg(path))

    def test_assembly_subset_as_svg(self):
        # A partial assembly should still flatten cleanly to a Compound
        # and emit valid SVG.
        path = export_assembly(
            self.assembler,
            self.tmp_dir / "subset.svg",
            parts=[Part.BOTTOM],
            file_format=".svg",
        )
        self.assertTrue(self._looks_like_svg(path))


if __name__ == "__main__":
    unittest.main()
