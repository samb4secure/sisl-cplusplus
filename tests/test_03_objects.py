"""
Test 03: Nested Objects
=======================
Tests for object/dictionary type conversions with various nesting levels.
"""

import pytest
import pysisl


class TestSimpleObjects:
    """Simple object conversions."""

    def test_empty_object(self, sislc):
        """Empty object."""
        obj = {}

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_single_key_object(self, sislc):
        """Object with single key."""
        obj = {"key": "value"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_multiple_keys_object(self, sislc):
        """Object with multiple keys."""
        obj = {"a": 1, "b": 2, "c": 3}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_mixed_value_types(self, sislc):
        """Object with different value types."""
        obj = {
            "string": "hello",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result["string"] == "hello"
        assert cpp_result["integer"] == 42
        assert abs(cpp_result["float"] - 3.14) < 0.001
        assert cpp_result["boolean"] == True
        assert cpp_result["null"] == None

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result["string"] == "hello"
        assert py_result["integer"] == 42
        assert abs(py_result["float"] - 3.14) < 0.001
        assert py_result["boolean"] == True
        assert py_result["null"] == None


class TestNestedObjects:
    """Nested object structures."""

    def test_one_level_nesting(self, sislc):
        """Object with one level of nesting."""
        obj = {"outer": {"inner": "value"}}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_two_level_nesting(self, sislc):
        """Object with two levels of nesting."""
        obj = {"a": {"b": {"c": "deep"}}}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_deep_nesting(self, sislc):
        """Object with deep nesting (5 levels)."""
        obj = {"l1": {"l2": {"l3": {"l4": {"l5": "bottom"}}}}}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_multiple_nested_siblings(self, sislc):
        """Object with multiple nested sibling objects."""
        obj = {
            "user": {"name": "Alice", "age": 30},
            "address": {"city": "NYC", "zip": "10001"}
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj


class TestObjectsWithArrays:
    """Objects containing arrays."""

    def test_object_with_array_value(self, sislc):
        """Object with array as value."""
        obj = {"numbers": [1, 2, 3]}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_nested_object_with_arrays(self, sislc):
        """Nested object containing arrays."""
        obj = {
            "data": {
                "values": [1, 2, 3],
                "labels": ["a", "b", "c"]
            }
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj


class TestSpecialKeyNames:
    """Objects with special key names."""

    def test_underscore_key(self, sislc):
        """Key starting with underscore."""
        obj = {"_private": "value"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_numeric_suffix_key(self, sislc):
        """Key with numeric suffix."""
        obj = {"item1": "a", "item2": "b", "item3": "c"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_dotted_key(self, sislc):
        """Key containing dots."""
        obj = {"config.setting": "value"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_hyphenated_key(self, sislc):
        """Key containing hyphens."""
        obj = {"my-key": "value"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_long_key(self, sislc):
        """Very long key name."""
        obj = {"a" * 100: "value"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj
