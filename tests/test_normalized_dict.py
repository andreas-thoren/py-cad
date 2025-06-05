import unittest
from py_cad.core import NormalizedDict


class TestNormalizedDict(unittest.TestCase):
    def setUp(self):
        self.d = NormalizedDict({" A ": 1, "b": 2})

    def test_getitem(self):
        self.assertEqual(self.d["a"], 1)
        self.assertEqual(self.d[" A "], 1)
        self.assertEqual(self.d["B"], 2)

    def test_setitem(self):
        self.d[" C "] = 3
        self.assertIn(" c ", self.d)  # Raw key still works because it normalizes
        self.assertEqual(self.d["C"], 3)
        self.assertEqual(self.d[" c "], 3)

    def test_delitem(self):
        del self.d[" A "]
        self.assertNotIn("a", self.d)
        self.assertNotIn(" A ", self.d)
        with self.assertRaises(KeyError):
            _ = self.d["a"]

    def test_contains(self):
        self.assertIn(" a ", self.d)
        self.assertIn("A", self.d)
        self.assertIn(" b ", self.d)
        self.assertNotIn(" c ", self.d)

    def test_get_method(self):
        self.assertEqual(self.d.get(" A "), 1)
        self.assertEqual(self.d.get("b"), 2)
        self.assertIsNone(self.d.get("nonexistent"))
        self.assertEqual(self.d.get("nonexistent", 99), 99)

    def test_pop_method(self):
        val = self.d.pop(" A ")
        self.assertEqual(val, 1)
        self.assertNotIn("a", self.d)

    def test_setdefault_method(self):
        val = self.d.setdefault(" D ", 4)
        self.assertEqual(val, 4)
        self.assertIn("d", self.d)
        # Should not overwrite existing
        val2 = self.d.setdefault(" d ", 99)
        self.assertEqual(val2, 4)

    def test_update_method(self):
        self.d.update({" E ": 5, " F ": 6})
        self.assertIn("e", self.d)
        self.assertIn("f", self.d)
        self.assertEqual(self.d[" e "], 5)
        self.assertEqual(self.d["f"], 6)

    def test_non_string_keys(self):
        with self.assertRaises(TypeError):
            self.d[10] = "number"
        self.assertNotIn(10, self.d)


if __name__ == "__main__":
    unittest.main()
