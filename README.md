# sisl-c++

A C++ application for serialising and deserialising SISL, compatible with [pysisl](https://pypi.org/project/pysisl/). Supports JSON and some support of XML as interchange formats.

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

The XML codec operates in two modes, selected automatically based on the input.

#### Typed XML (JSON-compatible)

Used when the input XML has a `<root>` element and its children carry `type` attributes. This mode preserves JSON data types exactly.

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

#### Generic XML (Arbitrary XML)

Used for any XML that doesn't match the typed format — for example, Windows Event Log exports, SOAP messages, configuration files, or any third-party XML. The codec converts the XML structure into a JSON representation that preserves tag names, attributes, text content, and element hierarchy.

```bash
# Convert arbitrary XML to SISL
./sislc --dumps --xml --input events.xml --output events.sisl

# Convert back to XML
./sislc --loads --xml --input events.sisl --output events_roundtrip.xml
```

The JSON representation uses these keys:

| Key | Present | Description |
|---|---|---|
| `_decl` | If XML declaration exists | Object of declaration attributes (`version`, `encoding`, `standalone`) |
| `_root` | Always | The root element (see below) |
| `_tag` | Always (on elements) | Element tag name |
| `_attrs` | If element has attributes | Object of attribute name-value pairs |
| `_text` | If element has text-only content | The text content as a string |
| `_children` | If element has child elements | Array of child element objects |

Example — this XML:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Events>
  <Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
    <System>
      <Provider Name="nssm"/>
      <EventID Qualifiers="16384">1008</EventID>
      <Security/>
    </System>
  </Event>
</Events>
```

Produces this JSON intermediate (shown as SISL):

```
{_decl: !obj {version: !str "1.0", encoding: !str "utf-8"},
 _root: !obj {_tag: !str "Events", _children: !list {
   _0: !obj {_tag: !str "Event", _attrs: !obj {xmlns: !str "http://..."}, _children: !list {
     _0: !obj {_tag: !str "System", _children: !list {
       _0: !obj {_tag: !str "Provider", _attrs: !obj {Name: !str "nssm"}},
       _1: !obj {_tag: !str "EventID", _attrs: !obj {Qualifiers: !str "16384"}, _text: !str "1008"},
       _2: !obj {_tag: !str "Security"}}}}}}}}
```

**Auto-detection rules:**

| Direction | Typed Mode | Generic Mode |
|---|---|---|
| XML to SISL | `<root>` element + first child has `type` attribute | Everything else |
| SISL to XML | JSON has no `_root` key | JSON has `_root` key |

#### Generic XML Limitations

The following XML features are not preserved through a generic round-trip:

| Feature | Behaviour |
|---|---|
| Mixed content (text between child elements) | Interleaved text nodes are dropped; only child elements are kept |
| XML comments (`<!-- ... -->`) | Silently stripped |
| Processing instructions (`<?target ...?>`) | Stripped (except the `<?xml?>` declaration) |
| CDATA sections (`<![CDATA[...]]>`) | Normalized to plain text |
| DOCTYPE declarations | Blocked (disabled for security) |
| Namespace-prefixed attribute names (`xmlns:prefix`) | Encoded to SISL but cannot be decoded back — colons in key names conflict with SISL's `:` separator |
| Whitespace-only text content | Dropped by the XML parser |
| `--max-length` splitting | Ineffective — the entire document nests under a single `_root` key, so the splitter cannot break it into smaller pieces |

**Formatting differences in output:**

The output XML is structurally equivalent to the input but may differ cosmetically:

- Indentation uses tabs (regardless of original indentation)
- Attributes always use double quotes
- Empty elements use self-closing form with a space (`<Tag />`)
- Attributes are always on the same line as the opening tag

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
