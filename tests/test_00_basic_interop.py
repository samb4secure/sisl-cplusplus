#!/usr/bin/env python3
"""Interoperability tests between sislc and pysisl 0.0.13"""

import subprocess
import json
import pysisl

SISLC = "./build/sislc"

def run_sislc_dumps(json_input, max_length=None):
    """Run sislc --dumps on JSON input"""
    cmd = [SISLC, "--dumps"]
    if max_length:
        cmd.extend(["--max-length", str(max_length)])
    result = subprocess.run(cmd, input=json_input, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"sislc --dumps failed: {result.stderr}")
    return result.stdout.strip()

def run_sislc_loads(sisl_input):
    """Run sislc --loads on SISL input"""
    result = subprocess.run([SISLC, "--loads"], input=sisl_input, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"sislc --loads failed: {result.stderr}")
    return json.loads(result.stdout.strip())

def test_basic_dumps():
    """Test 1: Basic dumps"""
    print("Test 1: Basic dumps")
    test_json = {"hello": "world"}

    cpp_sisl = run_sislc_dumps(json.dumps(test_json))
    py_sisl = pysisl.dumps(test_json)

    print(f"  JSON: {test_json}")
    print(f"  C++ SISL: {cpp_sisl}")
    print(f"  Python SISL: {py_sisl}")

    assert cpp_sisl == py_sisl, f"Mismatch: C++ '{cpp_sisl}' != Python '{py_sisl}'"
    print("  PASS")

def test_basic_loads():
    """Test 2: Basic loads"""
    print("Test 2: Basic loads")
    sisl_str = '{name: !str "helpful_name", flag: !bool "false", count: !int "3"}'

    cpp_json = run_sislc_loads(sisl_str)
    py_json = pysisl.loads(sisl_str)

    print(f"  SISL: {sisl_str}")
    print(f"  C++ JSON: {cpp_json}")
    print(f"  Python JSON: {py_json}")

    assert cpp_json == py_json, f"Mismatch: C++ {cpp_json} != Python {py_json}"
    print("  PASS")

def test_list_encoding():
    """Test 3: Lists encoding"""
    print("Test 3: Lists encoding")
    test_json = {"field_one": [1, 2, 3]}

    cpp_sisl = run_sislc_dumps(json.dumps(test_json))
    py_sisl = pysisl.dumps(test_json)

    print(f"  JSON: {test_json}")
    print(f"  C++ SISL: {cpp_sisl}")
    print(f"  Python SISL: {py_sisl}")

    assert cpp_sisl == py_sisl, f"Mismatch: C++ '{cpp_sisl}' != Python '{py_sisl}'"
    print("  PASS")

def test_splitting():
    """Test 4: Splitting example"""
    print("Test 4: Splitting example")
    test_json = {"abc": 2, "def": 3}

    cpp_result = run_sislc_dumps(json.dumps(test_json), max_length=20)
    py_result = pysisl.dumps(test_json, max_length=20)

    print(f"  JSON: {test_json}")
    print(f"  C++ result: {cpp_result}")
    print(f"  Python result: {py_result}")

    # Parse the C++ result as JSON array of strings
    cpp_parts = json.loads(cpp_result)

    assert cpp_parts == py_result, f"Mismatch: C++ {cpp_parts} != Python {py_result}"
    print("  PASS")

def test_joining_example_1():
    """Test 5a: Joining example 1"""
    print("Test 5a: Joining example 1")
    sisl_parts = [
        '{abc: !list {_0: !str "I", _1: !list {_0: !str "am"}}}',
        '{abc: !list {_1: !list {_1: !str "a"}, _2: !str "list"}}'
    ]

    cpp_json = run_sislc_loads(json.dumps(sisl_parts))
    py_json = pysisl.loads(sisl_parts)

    print(f"  SISL parts: {sisl_parts}")
    print(f"  C++ JSON: {cpp_json}")
    print(f"  Python JSON: {py_json}")

    assert cpp_json == py_json, f"Mismatch: C++ {cpp_json} != Python {py_json}"
    print("  PASS")

def test_joining_example_2():
    """Test 5b: Joining example 2"""
    print("Test 5b: Joining example 2")
    sisl_parts = [
        '{abc: !list {_0: !str "I", _1: !list {_0: !str "am"}}}',
        '{abc: !list {_2: !list {_0: !str "a"}, _3: !str "list"}}'
    ]

    cpp_json = run_sislc_loads(json.dumps(sisl_parts))
    py_json = pysisl.loads(sisl_parts)

    print(f"  SISL parts: {sisl_parts}")
    print(f"  C++ JSON: {cpp_json}")
    print(f"  Python JSON: {py_json}")

    assert cpp_json == py_json, f"Mismatch: C++ {cpp_json} != Python {py_json}"
    print("  PASS")

def test_roundtrip_simple():
    """Test 6a: Simple round-trip"""
    print("Test 6a: Simple round-trip")
    test_cases = [
        {"hello": "world"},
        {"count": 42},
        {"pi": 3.14},
        {"flag": True},
        {"empty": None},
        {"list": [1, 2, 3]},
        {"nested": {"a": {"b": 1}}},
    ]

    for test_json in test_cases:
        json_str = json.dumps(test_json)
        cpp_sisl = run_sislc_dumps(json_str)
        cpp_roundtrip = run_sislc_loads(cpp_sisl)

        # For floats, compare with tolerance
        if test_json == {"pi": 3.14}:
            assert abs(cpp_roundtrip["pi"] - 3.14) < 0.001
        else:
            assert cpp_roundtrip == test_json, f"Round-trip failed for {test_json}: got {cpp_roundtrip}"

    print("  PASS")

def test_cross_roundtrip():
    """Test 6b: Cross-implementation round-trip"""
    print("Test 6b: Cross-implementation round-trip")
    test_json = {"name": "test", "values": [1, 2, 3], "nested": {"x": 10}}

    # Python dumps -> C++ loads
    py_sisl = pysisl.dumps(test_json)
    cpp_json = run_sislc_loads(py_sisl)
    assert cpp_json == test_json, f"Python->C++ failed: got {cpp_json}"

    # C++ dumps -> Python loads
    cpp_sisl = run_sislc_dumps(json.dumps(test_json))
    py_json = pysisl.loads(cpp_sisl)
    assert py_json == test_json, f"C++->Python failed: got {py_json}"

    print("  PASS")

def test_split_join_roundtrip():
    """Test 6c: Split then join round-trip"""
    print("Test 6c: Split then join round-trip")
    test_json = {"a": 1, "b": 2, "c": 3, "d": 4}

    # C++ dumps with split -> C++ loads with join
    cpp_split = run_sislc_dumps(json.dumps(test_json), max_length=20)
    cpp_parts = json.loads(cpp_split)
    cpp_joined = run_sislc_loads(json.dumps(cpp_parts))
    assert cpp_joined == test_json, f"C++ split/join failed: got {cpp_joined}"

    # Python dumps with split -> C++ loads with join
    py_split = pysisl.dumps(test_json, max_length=20)
    cpp_from_py = run_sislc_loads(json.dumps(py_split))
    assert cpp_from_py == test_json, f"Python split -> C++ join failed: got {cpp_from_py}"

    # C++ dumps with split -> Python loads with join
    py_from_cpp = pysisl.loads(cpp_parts)
    assert py_from_cpp == test_json, f"C++ split -> Python join failed: got {py_from_cpp}"

    print("  PASS")

def main():
    print("=" * 60)
    print("SISL Interoperability Tests (sislc vs pysisl 0.0.13)")
    print("=" * 60)
    print()

    tests = [
        test_basic_dumps,
        test_basic_loads,
        test_list_encoding,
        test_splitting,
        test_joining_example_1,
        test_joining_example_2,
        test_roundtrip_simple,
        test_cross_roundtrip,
        test_split_join_roundtrip,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
