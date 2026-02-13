# sisl-c++

A C++ application for serialising and deserialising SISL, compatible with [pysisl](https://pypi.org/project/pysisl/). Supports JSON and XML as interchange formats.

## What is SISL?

SISL (Simple Information Serialisation Language) is a structured data format designed for use in the [NCSC Safely Importing Data Pattern](https://www.ncsc.gov.uk/guidance/pattern-safely-importing-data). It provides a simple, verifiable format for transferring structured data across trust boundaries.

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

### Command Reference

```
sislc --dumps [--xml] [--max-length N] [--input FILE] [--output FILE]
sislc --loads [--xml] [--input FILE] [--output FILE]
```

| Flags | Input | Output |
|---|---|---|
| `--dumps` | JSON | SISL |
| `--dumps --xml` | XML | SISL |
| `--dumps --max-length N` | JSON | JSON array of SISL fragments |
| `--dumps --xml --max-length N` | XML | JSON array of SISL fragments |
| `--loads` | SISL | JSON |
| `--loads --xml` | SISL | XML |

By default, input is read from stdin and output is written to stdout. Use `--input FILE` and `--output FILE` to read/write files instead.

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

For large objects, use `--max-length` to split the output into multiple SISL fragments:

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

### XML Mode (`--xml`)

Use `--xml` to work with XML instead of JSON as the interchange format. This works with both `--dumps` (XML input) and `--loads` (XML output), and can be combined with `--max-length` for splitting.

#### Convert XML to SISL

```bash
echo '<root><name type="str">Alice</name><age type="int">30</age></root>' | ./sislc --dumps --xml
# Output: {name: !str "Alice", age: !int "30"}
```

#### Convert SISL to XML

```bash
echo '{name: !str "Alice", age: !int "30"}' | ./sislc --loads --xml
```

Output:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
  <name type="str">Alice</name>
  <age type="int">30</age>
</root>
```

#### Split XML input into SISL fragments

```bash
echo '<root><a type="str">value1</a><b type="str">value2</b></root>' | ./sislc --dumps --xml --max-length 50
```

#### Merge SISL fragments to XML

```bash
echo '["{a: !str \"1\"}", "{b: !str \"2\"}"]' | ./sislc --loads --xml
```

### File Input/Output (`--input`, `--output`)

Use `--input` and `--output` to work with files instead of stdin/stdout.

```bash
# Convert a JSON file to a SISL file
./sislc --dumps --input data.json --output data.sisl

# Convert a SISL file to a JSON file
./sislc --loads --input data.sisl --output data.json

# Convert an XML file to a SISL file
./sislc --dumps --xml --input data.xml --output data.sisl

# Convert a SISL file to an XML file
./sislc --loads --xml --input data.sisl --output data.xml
```

Both flags are optional and can be used independently — for example, `--input` with stdout, or stdin with `--output`.

### XML Format

The XML format uses a `<root>` element. Each child element carries a `type` attribute to preserve the data type through serialisation.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
  <name type="str">Alice</name>
  <age type="int">30</age>
  <active type="bool">true</active>
  <empty type="null"/>
  <items type="list">
    <item type="int">1</item>
    <item type="str">two</item>
  </items>
  <address type="obj">
    <city type="str">London</city>
  </address>
</root>
```

| Type Attribute | JSON Equivalent | Notes |
|---|---|---|
| `str` | string | Text content is the string value |
| `int` | integer | Text content is the decimal integer |
| `float` | number | Text content is the decimal float |
| `bool` | boolean | Text content is `true` or `false` |
| `null` | null | Self-closing element, no text content |
| `list` | array | Children are `<item>` elements, order from document order |
| `obj` | object | Children are named elements |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Parse error (invalid JSON, SISL, or XML) |
| 3 | Internal error |

## Differences from pysisl

This implementation focuses on JSON/XML-SISL conversion via command line. Features unique to sislc:

- XML as an interchange format (`--xml`)

Some pysisl features not included:

- XOR wrapping (`SislWrapper`)
- JSON schema validation on load
- Python-specific type handling

## See Also

- [pysisl on PyPI](https://pypi.org/project/pysisl/) - Python implementation
- [NCSC Safely Importing Data Pattern](https://www.ncsc.gov.uk/guidance/pattern-safely-importing-data)

## License

MIT LICENSE

See LICENSE file for details.
