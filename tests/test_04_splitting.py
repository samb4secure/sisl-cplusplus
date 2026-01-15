"""
Test 04: Splitting
==================
Tests for the max_length splitting behavior that divides large objects
into multiple SISL strings.
"""

import pytest
import pysisl
import json


class TestBasicSplitting:
    """Basic splitting functionality."""

    def test_no_split_needed(self, sislc):
        """Small object that fits in max_length."""
        obj = {"a": 1}

        cpp_result = sislc.dumps(obj, max_length=100)
        py_result = pysisl.dumps(obj, max_length=100)

        # C++ returns a single string when no split needed
        assert isinstance(cpp_result, str)
        # pysisl always returns a list when max_length is specified
        assert isinstance(py_result, list)
        # But the content should match
        assert cpp_result == py_result[0]

    def test_simple_split(self, sislc):
        """Simple object that needs splitting."""
        obj = {"abc": 2, "def": 3}

        cpp_parts = sislc.dumps(obj, max_length=20)
        py_parts = pysisl.dumps(obj, max_length=20)

        assert isinstance(cpp_parts, list)
        assert isinstance(py_parts, list)
        assert len(cpp_parts) == len(py_parts)
        assert cpp_parts == py_parts

    def test_split_three_keys(self, sislc):
        """Object with three keys that splits into three parts."""
        obj = {"a": 1, "b": 2, "c": 3}

        cpp_parts = sislc.dumps(obj, max_length=18)
        py_parts = pysisl.dumps(obj, max_length=18)

        assert len(cpp_parts) == len(py_parts)
        assert cpp_parts == py_parts


class TestSplitRoundTrip:
    """Split then join round-trip tests."""

    def test_split_join_simple(self, sislc):
        """Split and join simple object."""
        obj = {"a": 1, "b": 2, "c": 3}

        # C++ split -> C++ join
        cpp_parts = sislc.dumps(obj, max_length=18)
        cpp_joined = sislc.loads(cpp_parts)
        assert cpp_joined == obj

        # Python split -> C++ join
        py_parts = pysisl.dumps(obj, max_length=18)
        cpp_from_py = sislc.loads(py_parts)
        assert cpp_from_py == obj

        # C++ split -> Python join
        py_from_cpp = pysisl.loads(cpp_parts)
        assert py_from_cpp == obj

    def test_split_join_strings(self, sislc):
        """Split and join object with string values."""
        obj = {"name": "Alice", "city": "NYC"}

        cpp_parts = sislc.dumps(obj, max_length=25)
        cpp_joined = sislc.loads(cpp_parts)
        assert cpp_joined == obj

        py_parts = pysisl.dumps(obj, max_length=25)
        py_from_cpp = pysisl.loads(cpp_parts)
        assert py_from_cpp == obj

    def test_split_join_many_keys(self, sislc):
        """Split and join object with many keys."""
        obj = {f"key{i}": i for i in range(10)}

        cpp_parts = sislc.dumps(obj, max_length=25)
        cpp_joined = sislc.loads(cpp_parts)
        assert cpp_joined == obj

        py_parts = pysisl.dumps(obj, max_length=25)
        cpp_from_py = sislc.loads(py_parts)
        assert cpp_from_py == obj


class TestSplitWithTypes:
    """Splitting with different value types."""

    def test_split_integers(self, sislc):
        """Split object with integer values."""
        obj = {"x": 100, "y": 200, "z": 300}

        cpp_parts = sislc.dumps(obj, max_length=20)
        py_parts = pysisl.dumps(obj, max_length=20)

        assert cpp_parts == py_parts

    def test_split_booleans(self, sislc):
        """Split object with boolean values."""
        obj = {"a": True, "b": False, "c": True}

        cpp_parts = sislc.dumps(obj, max_length=25)
        py_parts = pysisl.dumps(obj, max_length=25)

        assert cpp_parts == py_parts

    def test_split_strings(self, sislc):
        """Split object with string values."""
        obj = {"x": "hello", "y": "world"}

        cpp_parts = sislc.dumps(obj, max_length=25)
        py_parts = pysisl.dumps(obj, max_length=25)

        assert cpp_parts == py_parts


class TestSplitEdgeCases:
    """Edge cases for splitting."""

    def test_exact_fit(self, sislc):
        """Object that exactly fits max_length."""
        obj = {"a": 1}
        sisl = pysisl.dumps(obj)
        exact_length = len(sisl)

        cpp_result = sislc.dumps(obj, max_length=exact_length)
        py_result = pysisl.dumps(obj, max_length=exact_length)

        # C++ returns a single string when no split needed
        assert isinstance(cpp_result, str)
        # pysisl always returns a list when max_length is specified
        assert isinstance(py_result, list)
        assert len(py_result) == 1

    def test_one_byte_over(self, sislc):
        """Object one byte over max_length."""
        obj = {"ab": 1, "cd": 2}
        sisl = pysisl.dumps(obj)
        length_minus_one = len(sisl) - 1

        cpp_parts = sislc.dumps(obj, max_length=length_minus_one)
        py_parts = pysisl.dumps(obj, max_length=length_minus_one)

        # Should split
        assert isinstance(cpp_parts, list)
        assert isinstance(py_parts, list)

    def test_split_preserves_order(self, sislc):
        """Splitting preserves key order when joined."""
        obj = {"first": 1, "second": 2, "third": 3}

        cpp_parts = sislc.dumps(obj, max_length=22)
        cpp_joined = sislc.loads(cpp_parts)

        # Check that keys are in original order
        assert list(cpp_joined.keys()) == ["first", "second", "third"]
