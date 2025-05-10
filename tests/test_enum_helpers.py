import unittest
from enum import StrEnum
from helpers.enum_helpers import create_str_enum, extend_str_enum


class TestEnumHelpers(unittest.TestCase):

    def test_create_enum_from_list(self):
        MyEnum = create_str_enum("MyEnum", ["apple", "banana"])
        self.assertTrue(issubclass(MyEnum, StrEnum))
        self.assertEqual(MyEnum.APPLE.value, "apple")
        self.assertEqual(MyEnum.BANANA.value, "banana")

    def test_extend_enum_successfully(self):
        BaseEnum = create_str_enum("BaseEnum", ["one", "two"])
        ExtendedEnum = extend_str_enum(
            BaseEnum, ["three", "four"], class_name="ExtendedEnum"
        )
        members = set(ExtendedEnum.__members__)
        self.assertEqual({"ONE", "TWO", "THREE", "FOUR"}, members)
        self.assertEqual(ExtendedEnum.THREE.value, "three")

    def test_extend_enum_with_enum(self):
        BaseEnum = create_str_enum("BaseEnum", ["apple"])
        NextEnum = create_str_enum("NextEnum", ["banana"])
        ExtEnum = extend_str_enum(BaseEnum, NextEnum)
        self.assertEqual(ExtEnum.APPLE.value, "apple")
        self.assertEqual(ExtEnum.BANANA.value, "banana")

    def test_extend_enum_succesful_key_replacement(self):
        BaseEnum = create_str_enum("BaseEnum", ["apple", "banana"])
        self.assertEqual(BaseEnum.BANANA, "banana")
        NextEnum = StrEnum("ExtEnum", {"BANANA": "banana2"})
        ExtEnum = extend_str_enum(BaseEnum, NextEnum)
        self.assertEqual(ExtEnum.BANANA, "banana2")


if __name__ == "__main__":
    unittest.main()
