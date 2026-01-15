"""
Test 08: Round-Trip Verification
================================
Tests that verify data survives complete round-trips through both implementations.
These tests ensure no data is lost or corrupted during encoding/decoding cycles.
"""

import pytest
import pysisl
import json


class TestSimpleRoundTrips:
    """Simple round-trip tests."""

    def test_cpp_roundtrip_string(self, sislc):
        """C++ round-trip for string."""
        original = {"key": "value"}
        sisl = sislc.dumps(original)
        result = sislc.loads(sisl)
        assert result == original

    def test_cpp_roundtrip_integer(self, sislc):
        """C++ round-trip for integer."""
        original = {"num": 42}
        sisl = sislc.dumps(original)
        result = sislc.loads(sisl)
        assert result == original

    def test_cpp_roundtrip_float(self, sislc):
        """C++ round-trip for float."""
        original = {"val": 3.14159}
        sisl = sislc.dumps(original)
        result = sislc.loads(sisl)
        assert abs(result["val"] - original["val"]) < 0.00001

    def test_cpp_roundtrip_boolean(self, sislc):
        """C++ round-trip for boolean."""
        original = {"flag": True}
        sisl = sislc.dumps(original)
        result = sislc.loads(sisl)
        assert result == original

    def test_cpp_roundtrip_null(self, sislc):
        """C++ round-trip for null."""
        original = {"empty": None}
        sisl = sislc.dumps(original)
        result = sislc.loads(sisl)
        assert result == original

    def test_cpp_roundtrip_array(self, sislc):
        """C++ round-trip for array."""
        original = {"items": [1, 2, 3]}
        sisl = sislc.dumps(original)
        result = sislc.loads(sisl)
        assert result == original

    def test_cpp_roundtrip_nested_object(self, sislc):
        """C++ round-trip for nested object."""
        original = {"outer": {"inner": "value"}}
        sisl = sislc.dumps(original)
        result = sislc.loads(sisl)
        assert result == original


class TestCrossImplementationRoundTrips:
    """Cross-implementation round-trips."""

    def test_py_to_cpp_to_py(self, sislc):
        """Python -> C++ -> Python round-trip."""
        original = {"name": "test", "values": [1, 2, 3]}

        py_sisl = pysisl.dumps(original)
        cpp_json = sislc.loads(py_sisl)
        cpp_sisl = sislc.dumps(cpp_json)
        final = pysisl.loads(cpp_sisl)

        assert final == original

    def test_cpp_to_py_to_cpp(self, sislc):
        """C++ -> Python -> C++ round-trip."""
        original = {"name": "test", "values": [1, 2, 3]}

        cpp_sisl = sislc.dumps(original)
        py_json = pysisl.loads(cpp_sisl)
        py_sisl = pysisl.dumps(py_json)
        final = sislc.loads(py_sisl)

        assert final == original

    def test_multiple_cross_trips(self, sislc):
        """Multiple cross-implementation round-trips."""
        original = {"data": {"items": [1, 2, 3], "count": 3}}

        current = original
        for _ in range(5):
            cpp_sisl = sislc.dumps(current)
            py_json = pysisl.loads(cpp_sisl)
            py_sisl = pysisl.dumps(py_json)
            cpp_json = sislc.loads(py_sisl)
            current = cpp_json

        assert current == original


class TestSplitJoinRoundTrips:
    """Round-trips involving splitting and joining."""

    def test_cpp_split_cpp_join(self, sislc):
        """C++ split then C++ join round-trip."""
        original = {"a": 1, "b": 2, "c": 3, "d": 4}

        parts = sislc.dumps(original, max_length=20)
        assert isinstance(parts, list)
        result = sislc.loads(parts)

        assert result == original

    def test_py_split_cpp_join(self, sislc):
        """Python split then C++ join round-trip."""
        original = {"a": 1, "b": 2, "c": 3, "d": 4}

        parts = pysisl.dumps(original, max_length=20)
        result = sislc.loads(parts)

        assert result == original

    def test_cpp_split_py_join(self, sislc):
        """C++ split then Python join round-trip."""
        original = {"a": 1, "b": 2, "c": 3, "d": 4}

        parts = sislc.dumps(original, max_length=20)
        result = pysisl.loads(parts)

        assert result == original

    def test_cross_split_join_multiple(self, sislc):
        """Multiple cross-implementation split/join cycles."""
        original = {"x": 10, "y": 20, "z": 30}

        # C++ split -> Python join -> Python split -> C++ join
        cpp_parts = sislc.dumps(original, max_length=20)
        py_json = pysisl.loads(cpp_parts)
        py_parts = pysisl.dumps(py_json, max_length=20)
        final = sislc.loads(py_parts)

        assert final == original


class TestComplexRoundTrips:
    """Round-trips with complex data structures."""

    def test_deeply_nested_roundtrip(self, sislc):
        """Round-trip for deeply nested structure."""
        original = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "value": "deep"
                        }
                    }
                }
            }
        }

        cpp_sisl = sislc.dumps(original)
        py_json = pysisl.loads(cpp_sisl)
        py_sisl = pysisl.dumps(py_json)
        result = sislc.loads(py_sisl)

        assert result == original

    def test_mixed_types_roundtrip(self, sislc):
        """Round-trip for structure with mixed types."""
        original = {
            "string": "hello",
            "int": 42,
            "bool": True,
            "null": None,
            "array": [1, "two", False],
            "object": {"nested": "value"}
        }

        cpp_sisl = sislc.dumps(original)
        py_json = pysisl.loads(cpp_sisl)
        py_sisl = pysisl.dumps(py_json)
        result = sislc.loads(py_sisl)

        assert result == original

    def test_large_array_roundtrip(self, sislc):
        """Round-trip for large array."""
        original = {"numbers": list(range(100))}

        cpp_sisl = sislc.dumps(original)
        result = sislc.loads(cpp_sisl)

        assert result == original

    def test_many_keys_roundtrip(self, sislc):
        """Round-trip for object with many keys."""
        original = {f"key{i}": f"value{i}" for i in range(50)}

        py_sisl = pysisl.dumps(original)
        result = sislc.loads(py_sisl)

        assert result == original


class TestEdgeCaseRoundTrips:
    """Round-trips for edge cases."""

    def test_empty_object_roundtrip(self, sislc):
        """Round-trip for empty object."""
        original = {}

        cpp_sisl = sislc.dumps(original)
        result = sislc.loads(cpp_sisl)

        assert result == original

    def test_empty_string_roundtrip(self, sislc):
        """Round-trip for empty string value."""
        original = {"empty": ""}

        cpp_sisl = sislc.dumps(original)
        result = sislc.loads(cpp_sisl)

        assert result == original

    def test_empty_array_roundtrip(self, sislc):
        """Round-trip for empty array."""
        original = {"arr": []}

        cpp_sisl = sislc.dumps(original)
        result = sislc.loads(cpp_sisl)

        assert result == original

    def test_special_chars_roundtrip(self, sislc):
        """Round-trip for strings with special characters."""
        original = {"text": 'Hello "World"\nNew\tLine\\Path'}

        cpp_sisl = sislc.dumps(original)
        py_json = pysisl.loads(cpp_sisl)
        py_sisl = pysisl.dumps(py_json)
        result = sislc.loads(py_sisl)

        assert result == original

    def test_large_integer_roundtrip(self, sislc):
        """Round-trip for large integers."""
        original = {"big": 9223372036854775807}

        cpp_sisl = sislc.dumps(original)
        result = sislc.loads(cpp_sisl)

        assert result == original

    def test_negative_integer_roundtrip(self, sislc):
        """Round-trip for negative integers."""
        original = {"negative": -9223372036854775808}

        cpp_sisl = sislc.dumps(original)
        result = sislc.loads(cpp_sisl)

        assert result == original
