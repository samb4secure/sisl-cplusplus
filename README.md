# sisl-c++

A C++ application for serialising and deserialising SISL, compatible with [pysisl](https://pypi.org/project/pysisl/).

## What is SISL?

SISL (Simple Information Serialisation Language) is a structured text format designed for use in the [NCSC Safely Importing Data Pattern](https://www.ncsc.gov.uk/guidance/pattern-safely-importing-data). It provides a simple, verifiable format for transferring structured data across trust boundaries.

SISL supports the "Transform - Verify" approach for safely handling untrusted external data. The format can be paired with hardware flow control devices for syntactic verification, making it suitable as an intermediate format in cross-classification communication architectures.

## SISL Syntax

SISL uses a structured key-value format enclosed in curly braces. The basic element structure is:

```
name: !type "value"
```

Multiple elements are comma-separated:

```
{name: !str "Alice", age: !int "30", active: !bool "true"}
```

### Supported Types

| JSON Type | SISL Type | Example |
|-----------|-----------|---------|
| string | `!str` | `name: !str "hello"` |
| integer | `!int` | `count: !int "42"` |
| float | `!float` | `price: !float "9.99"` |
| boolean | `!bool` | `active: !bool "true"` |
| null | `!null` | `empty: !null ""` |
| array | `!list` | `items: !list {_0: !int "1", _1: !int "2"}` |
| object | `!obj` | `data: !obj {key: !str "value"}` |

Arrays use indexed keys (`_0`, `_1`, `_2`, ...) within a `!list` grouping.

## Building

### Requirements

- CMake 3.14+
- C++17 compatible compiler

### Build Steps

```bash
mkdir build && cd build
cmake ..
make
```

The executable will be created at `build/sislc`.

### Install

```bash
cmake --install . --prefix /usr/local
```

## Usage

### Convert JSON to SISL (`--dumps`)

```bash
echo '{"name": "Alice", "age": 30}' | ./sislc --dumps
# Output: {name: !str "Alice", age: !int "30"}
```

### Convert SISL to JSON (`--loads`)

```bash
echo '{name: !str "Alice", age: !int "30"}' | ./sislc --loads
# Output: {"name":"Alice","age":30}
```

### Nested Structures

```bash
echo '{"user": {"name": "Bob"}, "tags": ["a", "b"]}' | ./sislc --dumps
# Output: {user: !obj {name: !str "Bob"}, tags: !list {_0: !str "a", _1: !str "b"}}
```

### Split Large Output (`--max-length`)

For large JSON objects, use `--max-length` to split the output into multiple SISL fragments:

```bash
echo '{"a": "value1", "b": "value2", "c": "value3"}' | ./sislc --dumps --max-length 50
```

When the output exceeds `max-length`, it returns a JSON array of SISL string fragments.

### Merge SISL Fragments

Pass a JSON array of SISL strings to `--loads` to automatically merge them:

```bash
echo '["{a: !str \"1\"}", "{b: !str \"2\"}"]' | ./sislc --loads
# Output: {"a":"1","b":"2"}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Parse error (invalid JSON or SISL) |
| 3 | Internal error |

## Differences from pysisl

This implementation focuses on JSON-SISL conversion via command line. Some pysisl features not included:

- XOR wrapping (`SislWrapper`)
- JSON schema validation on load
- Python-specific type handling

## See Also

- [pysisl on PyPI](https://pypi.org/project/pysisl/) - Python implementation
- [NCSC Safely Importing Data Pattern](https://www.ncsc.gov.uk/guidance/pattern-safely-importing-data)

## License

MIT LICENSE

See LICENSE file for details.
