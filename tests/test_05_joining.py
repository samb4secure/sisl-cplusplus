"""
Test 05: Joining
================
Tests for the joining behavior when multiple SISL strings are merged.
This includes the documented examples and various merge scenarios.
"""

import pytest
import pysisl


class TestDocumentedExamples:
    """Tests for the exact examples from pysisl documentation."""

    def test_joining_example_1(self, sislc):
        """First joining example from documentation.

        pysisl.loads([
            '{abc: !list {_0: !str "I", _1: !list {_0: !str "am"}}}',
            '{abc: !list {_1: !list {_1: !str "a"}, _2: !str "list"}}'
        ]) -> {"abc": ['I', ['am', 'a'], 'list']}
        """
        sisl_parts = [
            '{abc: !list {_0: !str "I", _1: !list {_0: !str "am"}}}',
            '{abc: !list {_1: !list {_1: !str "a"}, _2: !str "list"}}'
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        expected = {"abc": ["I", ["am", "a"], "list"]}
        assert cpp_result == expected
        assert py_result == expected
        assert cpp_result == py_result

    def test_joining_example_2(self, sislc):
        """Second joining example from documentation.

        pysisl.loads([
            '{abc: !list {_0: !str "I", _1: !list {_0: !str "am"}}}',
            '{abc: !list {_2: !list {_0: !str "a"}, _3: !str "list"}}'
        ]) -> {"abc": ['I', ['am'], ['a'], 'list']}
        """
        sisl_parts = [
            '{abc: !list {_0: !str "I", _1: !list {_0: !str "am"}}}',
            '{abc: !list {_2: !list {_0: !str "a"}, _3: !str "list"}}'
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        expected = {"abc": ["I", ["am"], ["a"], "list"]}
        assert cpp_result == expected
        assert py_result == expected
        assert cpp_result == py_result


class TestSimpleJoining:
    """Simple joining scenarios."""

    def test_join_two_disjoint_keys(self, sislc):
        """Join two documents with different keys."""
        sisl_parts = [
            '{a: !int "1"}',
            '{b: !int "2"}'
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        expected = {"a": 1, "b": 2}
        assert cpp_result == expected
        assert py_result == expected

    def test_join_three_disjoint_keys(self, sislc):
        """Join three documents with different keys."""
        sisl_parts = [
            '{a: !int "1"}',
            '{b: !int "2"}',
            '{c: !int "3"}'
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        expected = {"a": 1, "b": 2, "c": 3}
        assert cpp_result == expected
        assert py_result == expected

    def test_join_overlapping_primitives(self, sislc):
        """Join documents where later values overwrite earlier ones."""
        sisl_parts = [
            '{a: !int "1"}',
            '{a: !int "2"}'
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        # Later value should win
        expected = {"a": 2}
        assert cpp_result == expected
        assert py_result == expected


class TestNestedJoining:
    """Joining with nested structures."""

    def test_join_nested_objects(self, sislc):
        """Join documents with nested objects."""
        sisl_parts = [
            '{outer: !obj {a: !int "1"}}',
            '{outer: !obj {b: !int "2"}}'
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        expected = {"outer": {"a": 1, "b": 2}}
        assert cpp_result == expected
        assert py_result == expected

    def test_join_deeply_nested(self, sislc):
        """Join deeply nested structures."""
        sisl_parts = [
            '{a: !obj {b: !obj {c: !int "1"}}}',
            '{a: !obj {b: !obj {d: !int "2"}}}'
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        expected = {"a": {"b": {"c": 1, "d": 2}}}
        assert cpp_result == expected
        assert py_result == expected


class TestListJoining:
    """Joining with list (array) structures."""

    def test_join_list_elements(self, sislc):
        """Join documents contributing to same list."""
        sisl_parts = [
            '{arr: !list {_0: !int "1"}}',
            '{arr: !list {_1: !int "2"}}'
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        expected = {"arr": [1, 2]}
        assert cpp_result == expected
        assert py_result == expected

    def test_join_sparse_list(self, sislc):
        """Join documents with sparse list indices (gaps)."""
        sisl_parts = [
            '{arr: !list {_0: !int "1"}}',
            '{arr: !list {_2: !int "3"}}'
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        # C++ fills gaps with null (as per spec)
        cpp_expected = {"arr": [1, None, 3]}
        assert cpp_result == cpp_expected

        # pysisl doesn't fill gaps in simple cases
        # Just verify pysisl gets the values
        assert 1 in py_result["arr"]
        assert 3 in py_result["arr"]

    def test_join_overlapping_list_indices(self, sislc):
        """Join documents with overlapping list indices."""
        sisl_parts = [
            '{arr: !list {_0: !int "1", _1: !int "2"}}',
            '{arr: !list {_1: !int "20", _2: !int "3"}}'
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        # Index 1 should be overwritten by second document
        expected = {"arr": [1, 20, 3]}
        assert cpp_result == expected
        assert py_result == expected

    def test_join_nested_lists(self, sislc):
        """Join documents with nested list merging."""
        sisl_parts = [
            '{arr: !list {_0: !list {_0: !int "1"}}}',
            '{arr: !list {_0: !list {_1: !int "2"}}}'
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        expected = {"arr": [[1, 2]]}
        assert cpp_result == expected
        assert py_result == expected


class TestComplexJoining:
    """Complex joining scenarios."""

    def test_join_mixed_structure(self, sislc):
        """Join documents with mixed objects and lists."""
        sisl_parts = [
            '{data: !obj {items: !list {_0: !str "a"}}}',
            '{data: !obj {items: !list {_1: !str "b"}, count: !int "2"}}'
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        expected = {"data": {"items": ["a", "b"], "count": 2}}
        assert cpp_result == expected
        assert py_result == expected

    def test_join_many_fragments(self, sislc):
        """Join many small fragments."""
        sisl_parts = [
            '{a: !int "1"}',
            '{b: !int "2"}',
            '{c: !int "3"}',
            '{d: !int "4"}',
            '{e: !int "5"}'
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        expected = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
        assert cpp_result == expected
        assert py_result == expected

    def test_join_preserves_order(self, sislc):
        """Joining preserves key order from first appearance."""
        sisl_parts = [
            '{first: !int "1"}',
            '{second: !int "2"}',
            '{first: !int "10"}'  # Updates first, but shouldn't move it
        ]

        cpp_result = sislc.loads(sisl_parts)
        py_result = pysisl.loads(sisl_parts)

        expected = {"first": 10, "second": 2}
        assert cpp_result == expected
        assert py_result == expected

        # Check key order
        assert list(cpp_result.keys()) == ["first", "second"]
        assert list(py_result.keys()) == ["first", "second"]
