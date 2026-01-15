"""
Test 01: Primitive Types
========================
Tests for basic primitive type conversions: strings, integers, floats, booleans, null.
These are the simplest possible SISL documents.
"""

import pytest
import pysisl


class TestStrings:
    """String type conversions."""

    def test_simple_string(self, sislc):
        """Simple ASCII string."""
        obj = {"name": "hello"}

        # pysisl -> sislc
        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        # sislc -> pysisl
        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_empty_string(self, sislc):
        """Empty string value."""
        obj = {"empty": ""}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_string_with_spaces(self, sislc):
        """String containing spaces."""
        obj = {"greeting": "hello world"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_string_with_special_chars(self, sislc):
        """String with special characters that need escaping."""
        obj = {"text": 'hello "world"'}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_string_with_backslash(self, sislc):
        """String containing backslash."""
        obj = {"path": "C:\\Users\\test"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_string_with_newline(self, sislc):
        """String containing newline."""
        obj = {"multiline": "line1\nline2"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_string_with_tab(self, sislc):
        """String containing tab character."""
        obj = {"tabbed": "col1\tcol2"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_long_string(self, sislc):
        """Long string value."""
        obj = {"long": "a" * 1000}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj


class TestIntegers:
    """Integer type conversions."""

    def test_zero(self, sislc):
        """Zero integer."""
        obj = {"zero": 0}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_positive_integer(self, sislc):
        """Positive integer."""
        obj = {"count": 42}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_negative_integer(self, sislc):
        """Negative integer."""
        obj = {"temp": -10}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_large_integer(self, sislc):
        """Large integer (within 64-bit range)."""
        obj = {"big": 9223372036854775807}  # max int64

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_large_negative_integer(self, sislc):
        """Large negative integer."""
        obj = {"big_neg": -9223372036854775808}  # min int64

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj


class TestFloats:
    """Float type conversions."""

    def test_simple_float(self, sislc):
        """Simple decimal float."""
        obj = {"pi": 3.14}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert abs(cpp_result["pi"] - 3.14) < 0.001

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert abs(py_result["pi"] - 3.14) < 0.001

    def test_zero_float(self, sislc):
        """Zero as float."""
        obj = {"zero": 0.0}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result["zero"] == 0.0

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result["zero"] == 0.0

    def test_negative_float(self, sislc):
        """Negative float."""
        obj = {"temp": -273.15}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert abs(cpp_result["temp"] - (-273.15)) < 0.001

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert abs(py_result["temp"] - (-273.15)) < 0.001

    def test_scientific_notation(self, sislc):
        """Float in scientific notation."""
        obj = {"avogadro": 6.022e23}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert abs(cpp_result["avogadro"] / 6.022e23 - 1) < 0.001

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert abs(py_result["avogadro"] / 6.022e23 - 1) < 0.001

    def test_small_float(self, sislc):
        """Very small float."""
        obj = {"tiny": 1e-10}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert abs(cpp_result["tiny"] / 1e-10 - 1) < 0.001

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert abs(py_result["tiny"] / 1e-10 - 1) < 0.001


class TestBooleans:
    """Boolean type conversions."""

    def test_true(self, sislc):
        """Boolean true."""
        obj = {"flag": True}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_false(self, sislc):
        """Boolean false."""
        obj = {"flag": False}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj


class TestNull:
    """Null type conversions."""

    def test_null(self, sislc):
        """Null value."""
        obj = {"empty": None}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj
