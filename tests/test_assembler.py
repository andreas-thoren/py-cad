import unittest
from cadquery import Assembly
from tests.test_project.project_data import DIMENSION_DATA, Part, PartType
from tests.test_project.assembly import PartialAssemblerOuterLeaf


class TestAssemblerABC(unittest.TestCase):
    def setUp(self):
        self.assembler = PartialAssemblerOuterLeaf(DIMENSION_DATA)

    def test_part_inheritance(self):
        # Test if all parts are correctly inherited
        actual_parts = frozenset(self.assembler._resolved_part_map.keys())
        expected_parts = frozenset(member.value for member in Part)
        self.assertEqual(actual_parts, expected_parts)

    def test_all_part_types_mapped(self):
        # Test if all part types are mapped correctly
        mapped_part_types = frozenset(self.assembler._resolved_part_map.values())
        all_part_types = frozenset(member.value for member in PartType)
        self.assertEqual(mapped_part_types, all_part_types)

    def test_get_resolved_metadata_map(self):
        # Test if resolved metadata map contains all parts
        metadata_map = self.assembler._get_resolved_metadata_map()
        self.assertEqual(len(metadata_map), len(Part))
        for part in Part:
            self.assertIn(part, metadata_map)
            self.assertIsInstance(metadata_map[part], dict)

    def test_assemble_all_parts(self):
        # Test assembling all parts
        assembly = self.assembler.assemble()
        self.assertIsInstance(assembly, Assembly)
        self.assertEqual(len(assembly.children), len(Part))

    def test_assemble_specific_parts(self):
        # Test assembling specific parts
        selected_parts = [Part.BOTTOM, Part.TOP]
        assembly = self.assembler.assemble(parts=selected_parts)
        self.assertIsInstance(assembly, Assembly)
        self.assertEqual(len(assembly.children), len(selected_parts))

    def test_get_assembly(self):
        # Test getting the assembly directly
        assembly = self.assembler.get_assembly(DIMENSION_DATA)
        self.assertIsInstance(assembly, Assembly)
        self.assertEqual(len(assembly.children), len(Part))

    def test_setup_attribute_removal(self):
        setup_attributes = self.assembler._setup_attributes
        for attr in setup_attributes:
            self.assertFalse(
                hasattr(self.assembler, attr),
                f"Attribute {attr} should not be present in the assembler instance.",
            )


if __name__ == "__main__":
    unittest.main()
