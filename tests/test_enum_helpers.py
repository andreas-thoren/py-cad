import unittest
from enum import StrEnum
from py_cad.enum_helpers import create_str_enum, extend_str_enum


class TestEnumHelpers(unittest.TestCase):

    def test_create_enum_from_list(self):
        MyEnum = create_str_enum("MyEnum", ["apple", "banana"])
        self.assertTrue(issubclass(MyEnum, StrEnum))
        self.assertEqual(MyEnum.APPLE.value, "apple")
        self.assertEqual(MyEnum.BANANA.value, "banana")

    def test_create_enum_from_dict(self):
        members = {"APPLE": "apple fruit", "BANANA": "yellow fruit"}
        MyEnum = create_str_enum("MyEnum", members, normalize_members=False)
        self.assertIn("APPLE", MyEnum.__members__)
        self.assertEqual(MyEnum.APPLE.value, "apple fruit")
        self.assertEqual(MyEnum.BANANA.value, "yellow fruit")

    def test_extend_enum_with_list(self):
        BaseEnum = create_str_enum("BaseEnum", ["one", "two"])
        ExtendedEnum = extend_str_enum(
            BaseEnum, ["three", "four"], class_name="ExtendedEnum"
        )
        members = set(ExtendedEnum.__members__)
        self.assertEqual({"ONE", "TWO", "THREE", "FOUR"}, members)
        self.assertEqual(ExtendedEnum.THREE.value, "three")

    def test_extend_enum_with_dict(self):
        BaseEnum = create_str_enum("BaseEnum", ["apple"])
        additions = {"BANANA": "banana fruit", "CHERRY": "red fruit"}
        ExtEnum = extend_str_enum(BaseEnum, additions, normalize_new_members=False)
        self.assertIn("APPLE", ExtEnum.__members__)
        self.assertIn("BANANA", ExtEnum.__members__)
        self.assertIn("CHERRY", ExtEnum.__members__)
        self.assertEqual(ExtEnum.BANANA.value, "banana fruit")
        self.assertEqual(ExtEnum.CHERRY.value, "red fruit")

    def test_extend_enum_with_enum(self):
        BaseEnum = create_str_enum("BaseEnum", ["apple"])
        NextEnum = create_str_enum("NextEnum", ["banana"])
        ExtEnum = extend_str_enum(BaseEnum, NextEnum)
        self.assertEqual(ExtEnum.APPLE.value, "apple")
        self.assertEqual(ExtEnum.BANANA.value, "banana")

    def test_extend_enum_with_replacement(self):
        BaseEnum = create_str_enum("BaseEnum", ["apple", "banana"])
        self.assertEqual(BaseEnum.BANANA, "banana")
        NextEnum = StrEnum("NextEnum", {"BANANA": "banana2"})
        ExtEnum = extend_str_enum(
            BaseEnum, NextEnum, class_name="ExtEnum", replace_dups=True
        )
        self.assertEqual(ExtEnum.BANANA, "banana2")

    def test_extend_enum_without_replacement(self):
        Base = create_str_enum("Base", ["apple"])
        Extended = extend_str_enum(Base, {"apple": "banana"}, replace_dups=False)
        self.assertEqual(Extended.APPLE.value, "apple")  # not replaced

    def test_create_enum_with_normalization(self):
        MyEnum = create_str_enum("MyEnum", [" Apple Pie "])
        self.assertIn("APPLE_PIE", MyEnum.__members__)
        self.assertEqual(MyEnum.APPLE_PIE.value, "apple pie")

    def test_extend_enum_without_normalization(self):
        BaseEnum = create_str_enum("BaseEnum", ["apple"])
        new_members = {" fruit Salad ": " FRUIT salad "}
        ExtEnum = extend_str_enum(BaseEnum, new_members, normalize_new_members=False)
        self.assertIn(" fruit Salad ", ExtEnum.__members__)
        self.assertEqual(ExtEnum.__members__[" fruit Salad "].value, " FRUIT salad ")


if __name__ == "__main__":
    unittest.main()
