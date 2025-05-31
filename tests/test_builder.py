import unittest
from cadquery import Workplane
from tests.test_project.project_data import DIMENSION_DATA, PartType
from tests.test_project.parts import PartialBuilderOuterLeaf


class TestBuilderABC(unittest.TestCase):
    def setUp(self):
        self.builder = PartialBuilderOuterLeaf(DIMENSION_DATA)

    def test_part_type_inheritance(self):
        actual_part_types = self.builder._resolved_part_types
        excpected_part_types = frozenset(member.value for member in PartType)
        self.assertEqual(actual_part_types, excpected_part_types)

    def test_build_part_valid(self):
        # Test valid part building
        for part_type in PartType:
            with self.subTest(part_type=part_type):
                result = self.builder.build_part(part_type)
                self.assertIsInstance(result, Workplane)

    def test_build_part_invalid(self):
        # Test invalid part type raises ValueError
        with self.assertRaises(ValueError):
            self.builder.build_part("invalid_part")

    def test_cache_solid(self):
        # Test caching functionality
        part_type = PartType.BOTTOM
        solid1 = self.builder.build_part(part_type, cached_solid=True)
        solid2 = self.builder.build_part(part_type, cached_solid=True)
        self.assertIs(solid1, solid2)

    def test_clear_cache(self):
        # Test clearing cache functionality
        part_type = PartType.BOTTOM
        solid1 = self.builder.build_part(part_type, cached_solid=True)
        self.builder.clear_cache()
        solid2 = self.builder.build_part(part_type, cached_solid=True)
        self.assertIsNot(solid1, solid2)

    def test_get_part(self):
        # Test getting a part directly
        part_type = PartType.BOTTOM
        part = self.builder.get_part(DIMENSION_DATA, part_type)
        self.assertIsInstance(part, Workplane)


if __name__ == "__main__":
    unittest.main()
