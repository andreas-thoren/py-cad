import unittest
from enum import auto
from py_cad import StrAutoEnum


class TestStrAutoEnum(unittest.TestCase):
    def setUp(self):
        class TestEnum(StrAutoEnum):
            BOTTOM = auto()
            LONG_SIDE = auto()
            LONG_SIDE_INVERSE = auto()
            SHORT_SIDE = auto()
            SHORT_SIDE_INVERSE = auto()
            TOP = auto()

        self.TestEnum = TestEnum

    def test_enum_values(self):
        expected_values = {
            "bottom",
            "long_side",
            "long_side_inverse",
            "short_side",
            "short_side_inverse",
            "top",
        }
        actual_values = {member.value for member in self.TestEnum}
        self.assertEqual(actual_values, expected_values)


if __name__ == "__main__":
    unittest.main()
