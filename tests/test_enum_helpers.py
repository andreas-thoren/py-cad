import unittest
from enum import StrEnum
from helpers.enum_helpers import create_str_enum, extend_str_enum


class TestEnumHelpers(unittest.TestCase):

    def test_create_enum_from_list(self):
        MyEnum = create_str_enum("MyEnum", ["apple", "banana"])
        self.assertTrue(issubclass(MyEnum, StrEnum))
        self.assertEqual(MyEnum.APPLE.value, "apple")
        self.assertEqual(MyEnum.BANANA.value, "banana")

    def test_create_enum_from_dict(self):
        members = {"APPLE": "apple", "BANANA": "banana"}
        MyEnum = create_str_enum("MyEnum", members)
        self.assertEqual(MyEnum.APPLE.value, "apple")
        self.assertEqual(MyEnum.BANANA.value, "banana")

    def test_duplicate_keys_in_list_raises(self):
        with self.assertRaises(ValueError) as cm:
            create_str_enum("BadEnum", ["apple", "Apple"])
        self.assertIn("keys", str(cm.exception))

    def test_duplicate_values_in_dict_raises(self):
        with self.assertRaises(ValueError) as cm:
            create_str_enum("BadEnum", {"ONE": "duplicate", "TWO": "duplicate"})
        self.assertIn("values", str(cm.exception))

    def test_extend_enum_successfully(self):
        BaseEnum = create_str_enum("BaseEnum", ["one", "two"])
        ExtendedEnum = extend_str_enum(
            BaseEnum, ["three", "four"], class_name="ExtendedEnum"
        )
        members = set(ExtendedEnum.__members__)
        self.assertEqual({"ONE", "TWO", "THREE", "FOUR"}, members)
        self.assertEqual(ExtendedEnum.THREE.value, "three")

    def test_extend_enum_with_key_conflict_raises(self):
        BaseEnum = create_str_enum("BaseEnum", ["apple"])
        with self.assertRaises(ValueError) as cm:
            extend_str_enum(BaseEnum, ["apple"])  # same key
        self.assertIn("keys", str(cm.exception))

    def test_extend_enum_succesful_key_replacement(self):
        BaseEnum = create_str_enum("BaseEnum", {"Apple": "apple", "Banana": "banana"})
        self.assertEqual(BaseEnum.Banana, "banana")
        ExtEnum = extend_str_enum(
            BaseEnum, {"Banana": "banana2"}, replace_dup_members=True
        )
        self.assertEqual(ExtEnum.Banana, "banana2")


if __name__ == "__main__":
    unittest.main()
