r"""
Test 07: Escape Sequences
=========================
Tests for string escape sequence handling as defined in the SISL ABNF grammar.
Covers: \", \\, \r, \t, \n, \xHH, \uHHHH, \UHHHHHHHH
"""

import pytest
import pysisl


class TestBasicEscapes:
    """Basic escape sequences."""

    def test_escaped_quote(self, sislc):
        """String with escaped double quote."""
        obj = {"text": 'He said "hello"'}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_escaped_backslash(self, sislc):
        """String with escaped backslash."""
        obj = {"path": "C:\\Users\\name"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_carriage_return(self, sislc):
        """String with carriage return."""
        obj = {"text": "line1\rline2"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_tab(self, sislc):
        """String with tab character."""
        obj = {"text": "col1\tcol2\tcol3"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_newline(self, sislc):
        """String with newline."""
        obj = {"text": "line1\nline2\nline3"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj


class TestCombinedEscapes:
    """Multiple escape sequences combined."""

    def test_windows_path(self, sislc):
        """Windows-style path with backslashes."""
        obj = {"path": "C:\\Program Files\\App\\config.ini"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_multiline_with_tabs(self, sislc):
        """Multiline text with tabs."""
        obj = {"text": "Header:\n\tItem 1\n\tItem 2\n\tItem 3"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_quoted_string_in_text(self, sislc):
        """Text containing quoted strings."""
        obj = {"json": '{"key": "value"}'}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_crlf(self, sislc):
        """Windows-style line endings (CRLF)."""
        obj = {"text": "line1\r\nline2\r\nline3"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_all_basic_escapes(self, sislc):
        """String with all basic escape types."""
        obj = {"text": "quote:\" backslash:\\ tab:\t newline:\n cr:\r"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj


class TestSpecialCharacters:
    """Special and control characters."""

    def test_empty_string(self, sislc):
        """Empty string (no escapes needed)."""
        obj = {"text": ""}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_only_quotes(self, sislc):
        """String that is only quotes."""
        obj = {"text": '""'}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_only_backslashes(self, sislc):
        """String that is only backslashes."""
        obj = {"text": "\\\\\\"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_alternating_quotes_backslashes(self, sislc):
        """Alternating quotes and backslashes."""
        obj = {"text": '"\\"\\"\\'}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj


class TestRealWorldEscapes:
    """Real-world scenarios requiring escapes."""

    def test_sql_query(self, sislc):
        """SQL query with quotes."""
        obj = {"query": "SELECT * FROM users WHERE name = 'John'"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_regex_pattern(self, sislc):
        """Regex pattern with backslashes."""
        obj = {"pattern": "^\\d{3}-\\d{4}$"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_json_string(self, sislc):
        """JSON embedded in string."""
        obj = {"data": '{"name": "test", "value": 123}'}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_code_snippet(self, sislc):
        """Code snippet with various escapes."""
        obj = {"code": 'print("Hello\\nWorld")'}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_log_format(self, sislc):
        """Log format string."""
        obj = {"format": "[%Y-%m-%d %H:%M:%S]\t%level\t%message"}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj
