import unittest
from helpers.models import BasicDimensionData, DimensionData


class TestBasicDimensionData(unittest.TestCase):

    def test_basic_init_and_attributes(self):
        data = BasicDimensionData(
            (1, 2, 3), a=10, b=20, freeze_existing_attributes=True
        )
        self.assertEqual(data.x_len, 1)
        self.assertEqual(data.y_len, 2)
        self.assertEqual(data.z_len, 3)
        self.assertEqual(data.a, 10)  # pylint: disable=no-member
        self.assertEqual(data.b, 20)  # pylint: disable=no-member
        self.assertTrue(data._freeze_existing_attributes)

    def test_frozen_after_init(self):
        data = BasicDimensionData((1, 2, 3), freeze_existing_attributes=True)
        self.new_attribute = 42  # Allowed adding new attributes
        with self.assertRaises(AttributeError):
            data.x_len = 5

    def test_setting_frozen_inside_init(self):
        class MyDim(BasicDimensionData):
            def __init__(self):
                self.special = 123
                super().__init__((4, 5, 6), freeze_existing_attributes=True)

        inst = MyDim()
        self.assertEqual(inst.special, 123)
        with self.assertRaises(AttributeError):
            inst.special = 456

    def test_no_changing_attributes_after_freeze(self):
        data = BasicDimensionData()
        # Should be able to add before freeze
        data.new_attr = 123
        data.new_attr = 234  # Allowed to change before freeze
        data.set_basic_dimensions((1, 2, 3))
        data.new_attr = 345  # Allowed to change before freeze
        data.freeze_existing_attributes()
        with self.assertRaises(AttributeError):
            data.new_attr = 456

    def test_freeze_without_basic_dimensions_raises(self):
        data = BasicDimensionData()
        with self.assertRaises(ValueError):
            data.freeze_existing_attributes()


class TestDimensionData(unittest.TestCase):

    class MyDimData(DimensionData):
        def get_part_types_dimensions(self):
            return {"foo": (1, 2, 3), "bar": (4, 5, 6)}

    def test_material_thickness_scalar(self):
        dim = self.MyDimData(10, 20, 30, mat_thickness=12)
        self.assertEqual(dim.mat_thickness, 12)

    def test_material_thickness_dict(self):
        dct = {"thickness": {"foo": 2, "bar": 5}}

        dim = self.MyDimData(1, 2, 3, part_type_attributes=dct)
        self.assertEqual(dim["foo"].thickness, 2)
        self.assertEqual(dim["bar"].thickness, 5)
        # Test normalization
        self.assertEqual(dim["FOO"].thickness, 2)
        self.assertEqual(dim["Bar "].thickness, 5)

    def test_bracket_access(self):
        dim = self.MyDimData(1, 2, 3, mat_thickness=8)
        self.assertIsInstance(dim["foo"], BasicDimensionData)
        self.assertEqual(dim["foo"].x_len, 1)
        self.assertEqual(dim["bar"].y_len, 5)
        with self.assertRaises(KeyError):
            _ = dim["baz"]

    def test_part_types_dimensions_type_check(self):
        # Should raise if get_part_types_dimensions returns invalid mapping
        class BadDim(DimensionData):
            def get_part_types_dimensions(self):
                return {"foo": 123}  # Not BasicDimensionData

        with self.assertRaises(TypeError):
            BadDim(1, 2, 3, mat_thickness=1)

    def test_subclass_without_get_part_types_dimensions(self):
        class NoOverrideDim(DimensionData):
            pass  # No get_part_types_dimensions

        # Should not raise
        dim = NoOverrideDim(1, 2, 3, mat_thickness=1)
        # Default is empty dict, so no parts accessible
        self.assertEqual(dim._part_types_dimensions, {})
        with self.assertRaises(KeyError):
            _ = dim["any_part"]

    def test_update_part_type_dim_formats(self):
        dim = BasicDimensionData()
        # Tuple format
        basic_dims, extra_dims = DimensionData._normalize_part_type_dimensions((1, 2, 3))
        dim.set_basic_dimensions(basic_dims, **extra_dims)
        self.assertEqual(dim.x_len, 1)
        self.assertEqual(dim.y_len, 2)
        self.assertEqual(dim.z_len, 3)
        # Tuple+dict format
        dim2 = BasicDimensionData()
        basic_dims, extra_dims = DimensionData._normalize_part_type_dimensions(
            ((4, 5, 6), {"foo": 99})
        )
        dim2.set_basic_dimensions(basic_dims, **extra_dims)
        self.assertEqual(dim2.x_len, 4)
        self.assertEqual(dim2.y_len, 5)
        self.assertEqual(dim2.z_len, 6)
        self.assertEqual(dim2.foo, 99)


if __name__ == "__main__":
    unittest.main()
