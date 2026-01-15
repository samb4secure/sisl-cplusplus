"""
Test 09: Exact SISL Format Matching
===================================
Tests that verify the exact SISL string format matches between implementations.
These tests ensure canonical formatting is identical.
"""

import pytest
import pysisl


class TestExactStringFormat:
    """Tests for exact string format matching."""

    def test_simple_string_format(self, sislc):
        """Exact format for simple string."""
        obj = {"hello": "world"}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        assert cpp_sisl == py_sisl
        assert cpp_sisl == '{hello: !str "world"}'

    def test_integer_format(self, sislc):
        """Exact format for integer."""
        obj = {"count": 42}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        assert cpp_sisl == py_sisl
        assert cpp_sisl == '{count: !int "42"}'

    def test_boolean_true_format(self, sislc):
        """Exact format for boolean true."""
        obj = {"flag": True}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        assert cpp_sisl == py_sisl
        assert cpp_sisl == '{flag: !bool "true"}'

    def test_boolean_false_format(self, sislc):
        """Exact format for boolean false."""
        obj = {"flag": False}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        assert cpp_sisl == py_sisl
        assert cpp_sisl == '{flag: !bool "false"}'

    def test_null_format(self, sislc):
        """Exact format for null."""
        obj = {"empty": None}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        assert cpp_sisl == py_sisl
        assert cpp_sisl == '{empty: !null ""}'


class TestListFormat:
    """Tests for exact list format matching."""

    def test_simple_list_format(self, sislc):
        """Exact format for simple list."""
        obj = {"items": [1, 2, 3]}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        assert cpp_sisl == py_sisl
        expected = '{items: !list {_0: !int "1", _1: !int "2", _2: !int "3"}}'
        assert cpp_sisl == expected

    def test_single_element_list_format(self, sislc):
        """Exact format for single element list."""
        obj = {"items": [42]}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        assert cpp_sisl == py_sisl
        assert cpp_sisl == '{items: !list {_0: !int "42"}}'

    def test_empty_list_format(self, sislc):
        """Exact format for empty list."""
        obj = {"items": []}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        assert cpp_sisl == py_sisl
        assert cpp_sisl == '{items: !list {}}'


class TestNestedObjectFormat:
    """Tests for exact nested object format matching."""

    def test_nested_object_format(self, sislc):
        """Exact format for nested object."""
        obj = {"outer": {"inner": "value"}}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        assert cpp_sisl == py_sisl
        expected = '{outer: !obj {inner: !str "value"}}'
        assert cpp_sisl == expected

    def test_deeply_nested_format(self, sislc):
        """Exact format for deeply nested object."""
        obj = {"a": {"b": {"c": 1}}}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        assert cpp_sisl == py_sisl
        expected = '{a: !obj {b: !obj {c: !int "1"}}}'
        assert cpp_sisl == expected


class TestMultipleKeysFormat:
    """Tests for exact format with multiple keys."""

    def test_two_keys_format(self, sislc):
        """Exact format for object with two keys."""
        obj = {"a": 1, "b": 2}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        assert cpp_sisl == py_sisl
        expected = '{a: !int "1", b: !int "2"}'
        assert cpp_sisl == expected

    def test_three_keys_format(self, sislc):
        """Exact format for object with three keys."""
        obj = {"x": "hello", "y": 42, "z": True}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        assert cpp_sisl == py_sisl

    def test_mixed_types_format(self, sislc):
        """Exact format for mixed types."""
        obj = {"str": "text", "num": 1, "bool": True, "nil": None}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        assert cpp_sisl == py_sisl


class TestDocumentedExamplesFormat:
    """Tests for exact format from documentation."""

    def test_documented_example_1(self, sislc):
        """First documented example: {"hello": "world"}"""
        obj = {"hello": "world"}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        expected = '{hello: !str "world"}'
        assert cpp_sisl == expected
        assert py_sisl == expected

    def test_documented_example_2(self, sislc):
        """Second documented example: list encoding"""
        obj = {"field_one": [1, 2, 3]}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        expected = '{field_one: !list {_0: !int "1", _1: !int "2", _2: !int "3"}}'
        assert cpp_sisl == expected
        assert py_sisl == expected

    def test_documented_example_3(self, sislc):
        """Third documented example: nested object"""
        obj = {"field_one": {"key_one": "teststring"}}

        cpp_sisl = sislc.dumps(obj)
        py_sisl = pysisl.dumps(obj)

        expected = '{field_one: !obj {key_one: !str "teststring"}}'
        assert cpp_sisl == expected
        assert py_sisl == expected


class TestSpacingFormat:
    """Tests for exact spacing in format."""

    def test_spacing_after_colon(self, sislc):
        """Verify single space after colon."""
        obj = {"key": "value"}

        cpp_sisl = sislc.dumps(obj)

        # Should have exactly one space after colon
        assert ": !" in cpp_sisl
        assert ":  !" not in cpp_sisl  # No double space

    def test_spacing_after_type(self, sislc):
        """Verify single space after type."""
        obj = {"key": "value"}

        cpp_sisl = sislc.dumps(obj)

        # Should have exactly one space after !str
        assert '!str "' in cpp_sisl
        assert '!str  "' not in cpp_sisl  # No double space

    def test_comma_spacing(self, sislc):
        """Verify comma followed by space."""
        obj = {"a": 1, "b": 2}

        cpp_sisl = sislc.dumps(obj)

        # Should have comma followed by space
        assert '", ' in cpp_sisl or '}, ' in cpp_sisl
