"""
Test 10: XML Support
=====================
Tests for XML input/output alongside JSON and SISL.
"""

import pytest
import xml.etree.ElementTree as ET


class TestXmlOutput:
    """Test SISL -> XML conversion (--loads --xml)."""

    def test_simple_string(self, sislc):
        """String value produces correct XML."""
        xml_out = sislc.loads_xml('{name: !str "Alice"}')
        root = ET.fromstring(xml_out)
        elem = root.find("name")
        assert elem is not None
        assert elem.get("type") == "str"
        assert elem.text == "Alice"

    def test_integer(self, sislc):
        """Integer value produces correct XML."""
        xml_out = sislc.loads_xml('{age: !int "30"}')
        root = ET.fromstring(xml_out)
        elem = root.find("age")
        assert elem.get("type") == "int"
        assert elem.text == "30"

    def test_float(self, sislc):
        """Float value produces correct XML."""
        xml_out = sislc.loads_xml('{price: !float "9.99"}')
        root = ET.fromstring(xml_out)
        elem = root.find("price")
        assert elem.get("type") == "float"
        assert float(elem.text) == pytest.approx(9.99)

    def test_boolean_true(self, sislc):
        """Boolean true produces correct XML."""
        xml_out = sislc.loads_xml('{active: !bool "true"}')
        root = ET.fromstring(xml_out)
        elem = root.find("active")
        assert elem.get("type") == "bool"
        assert elem.text == "true"

    def test_boolean_false(self, sislc):
        """Boolean false produces correct XML."""
        xml_out = sislc.loads_xml('{active: !bool "false"}')
        root = ET.fromstring(xml_out)
        elem = root.find("active")
        assert elem.get("type") == "bool"
        assert elem.text == "false"

    def test_null(self, sislc):
        """Null value produces self-closing XML element."""
        xml_out = sislc.loads_xml('{empty: !null ""}')
        root = ET.fromstring(xml_out)
        elem = root.find("empty")
        assert elem.get("type") == "null"
        assert elem.text is None

    def test_list(self, sislc):
        """List produces <item> children."""
        xml_out = sislc.loads_xml('{items: !list {_0: !int "1", _1: !str "two"}}')
        root = ET.fromstring(xml_out)
        items_elem = root.find("items")
        assert items_elem.get("type") == "list"
        children = list(items_elem)
        assert len(children) == 2
        assert children[0].tag == "item"
        assert children[0].get("type") == "int"
        assert children[0].text == "1"
        assert children[1].tag == "item"
        assert children[1].get("type") == "str"
        assert children[1].text == "two"

    def test_nested_object(self, sislc):
        """Nested object produces correct XML structure."""
        xml_out = sislc.loads_xml('{address: !obj {city: !str "London"}}')
        root = ET.fromstring(xml_out)
        addr = root.find("address")
        assert addr.get("type") == "obj"
        city = addr.find("city")
        assert city.get("type") == "str"
        assert city.text == "London"

    def test_xml_declaration(self, sislc):
        """Output starts with XML declaration."""
        xml_out = sislc.loads_xml('{x: !int "1"}')
        assert xml_out.startswith("<?xml")

    def test_root_element(self, sislc):
        """Output has <root> as the top-level element."""
        xml_out = sislc.loads_xml('{x: !int "1"}')
        root = ET.fromstring(xml_out)
        assert root.tag == "root"

    def test_multiple_fields(self, sislc):
        """Multiple top-level fields."""
        xml_out = sislc.loads_xml('{name: !str "Alice", age: !int "30"}')
        root = ET.fromstring(xml_out)
        assert root.find("name").text == "Alice"
        assert root.find("age").text == "30"


class TestXmlInput:
    """Test XML -> SISL conversion (--dumps --xml)."""

    def test_simple_string(self, sislc):
        """XML string input converts to SISL."""
        xml_input = '<?xml version="1.0"?><root><name type="str">Alice</name></root>'
        sisl_out = sislc.dumps_xml(xml_input)
        result = sislc.loads(sisl_out)
        assert result == {"name": "Alice"}

    def test_integer(self, sislc):
        """XML integer input converts correctly."""
        xml_input = '<root><age type="int">30</age></root>'
        sisl_out = sislc.dumps_xml(xml_input)
        result = sislc.loads(sisl_out)
        assert result == {"age": 30}

    def test_float(self, sislc):
        """XML float input converts correctly."""
        xml_input = '<root><price type="float">9.99</price></root>'
        sisl_out = sislc.dumps_xml(xml_input)
        result = sislc.loads(sisl_out)
        assert result["price"] == pytest.approx(9.99)

    def test_boolean(self, sislc):
        """XML boolean input converts correctly."""
        xml_input = '<root><active type="bool">true</active></root>'
        sisl_out = sislc.dumps_xml(xml_input)
        result = sislc.loads(sisl_out)
        assert result == {"active": True}

    def test_null(self, sislc):
        """XML null input converts correctly."""
        xml_input = '<root><empty type="null"/></root>'
        sisl_out = sislc.dumps_xml(xml_input)
        result = sislc.loads(sisl_out)
        assert result == {"empty": None}

    def test_list(self, sislc):
        """XML list input converts correctly."""
        xml_input = '<root><items type="list"><item type="int">1</item><item type="str">two</item></items></root>'
        sisl_out = sislc.dumps_xml(xml_input)
        result = sislc.loads(sisl_out)
        assert result == {"items": [1, "two"]}

    def test_nested_object(self, sislc):
        """XML nested object converts correctly."""
        xml_input = '<root><address type="obj"><city type="str">London</city></address></root>'
        sisl_out = sislc.dumps_xml(xml_input)
        result = sislc.loads(sisl_out)
        assert result == {"address": {"city": "London"}}

    def test_multiple_fields(self, sislc):
        """XML with multiple fields converts correctly."""
        xml_input = '<root><name type="str">Alice</name><age type="int">30</age></root>'
        sisl_out = sislc.dumps_xml(xml_input)
        result = sislc.loads(sisl_out)
        assert result == {"name": "Alice", "age": 30}


class TestXmlRoundTrips:
    """Test round-trip conversions involving XML."""

    def test_json_to_sisl_to_xml(self, sislc):
        """JSON -> SISL -> XML preserves data."""
        obj = {"name": "Alice", "age": 30, "active": True}
        sisl_str = sislc.dumps(obj)
        xml_out = sislc.loads_xml(sisl_str)
        root = ET.fromstring(xml_out)
        assert root.find("name").text == "Alice"
        assert root.find("age").text == "30"
        assert root.find("active").text == "true"

    def test_xml_to_sisl_to_json(self, sislc):
        """XML -> SISL -> JSON preserves data."""
        xml_input = '<root><name type="str">Bob</name><count type="int">42</count></root>'
        sisl_str = sislc.dumps_xml(xml_input)
        result = sislc.loads(sisl_str)
        assert result == {"name": "Bob", "count": 42}

    def test_xml_to_sisl_to_xml(self, sislc):
        """XML -> SISL -> XML round-trip preserves data."""
        xml_input = '<root><name type="str">Alice</name><age type="int">30</age></root>'
        sisl_str = sislc.dumps_xml(xml_input)
        xml_out = sislc.loads_xml(sisl_str)
        root = ET.fromstring(xml_out)
        assert root.find("name").text == "Alice"
        assert root.find("age").text == "30"

    def test_all_types_roundtrip(self, sislc):
        """Round-trip with all supported types."""
        obj = {
            "s": "hello",
            "i": 42,
            "f": 3.14,
            "b": True,
            "n": None,
            "l": [1, "two"],
            "o": {"nested": "value"},
        }
        sisl_str = sislc.dumps(obj)
        xml_out = sislc.loads_xml(sisl_str)
        sisl_str2 = sislc.dumps_xml(xml_out)
        result = sislc.loads(sisl_str2)
        assert result["s"] == "hello"
        assert result["i"] == 42
        assert result["f"] == pytest.approx(3.14)
        assert result["b"] is True
        assert result["n"] is None
        assert result["l"] == [1, "two"]
        assert result["o"] == {"nested": "value"}


class TestXmlWithSplitting:
    """Test XML input combined with --max-length splitting."""

    def test_split_from_xml(self, sislc):
        """XML input with --max-length produces split SISL fragments."""
        xml_input = '<root><a type="str">value1</a><b type="str">value2</b><c type="str">value3</c></root>'
        result = sislc.dumps_xml(xml_input, max_length=50)
        assert isinstance(result, list)
        assert len(result) >= 2
        # Merge fragments and verify data
        merged = sislc.loads(result)
        assert merged["a"] == "value1"
        assert merged["b"] == "value2"
        assert merged["c"] == "value3"

    def test_small_xml_no_split(self, sislc):
        """Small XML input with large max-length produces single SISL string."""
        xml_input = '<root><x type="int">1</x></root>'
        result = sislc.dumps_xml(xml_input, max_length=1000)
        assert isinstance(result, str)
        loaded = sislc.loads(result)
        assert loaded == {"x": 1}


class TestXmlMergeToXml:
    """Test merging SISL fragments to XML output."""

    def test_merge_fragments_to_xml(self, sislc):
        """Merging SISL fragments with --loads --xml produces valid XML."""
        obj = {"a": "value1", "b": "value2", "c": "value3"}
        fragments = sislc.dumps(obj, max_length=50)
        assert isinstance(fragments, list)
        xml_out = sislc.loads_xml(fragments)
        root = ET.fromstring(xml_out)
        assert root.find("a").text == "value1"
        assert root.find("b").text == "value2"
        assert root.find("c").text == "value3"


class TestXmlErrors:
    """Test error handling for XML operations."""

    def test_invalid_xml(self, sislc):
        """Invalid XML produces an error."""
        with pytest.raises(RuntimeError, match="--dumps --xml failed"):
            sislc.dumps_xml("<not-closed>")

    def test_missing_root(self, sislc):
        """XML without <root> element produces an error."""
        with pytest.raises(RuntimeError, match="--dumps --xml failed"):
            sislc.dumps_xml('<?xml version="1.0"?><data><x type="str">y</x></data>')

    def test_missing_type_attribute(self, sislc):
        """Element without type attribute produces an error."""
        with pytest.raises(RuntimeError, match="--dumps --xml failed"):
            sislc.dumps_xml("<root><name>Alice</name></root>")

    def test_invalid_type(self, sislc):
        """Unknown type attribute produces an error."""
        with pytest.raises(RuntimeError, match="--dumps --xml failed"):
            sislc.dumps_xml('<root><x type="unknown">val</x></root>')

    def test_invalid_int_value(self, sislc):
        """Non-numeric integer value produces an error."""
        with pytest.raises(RuntimeError, match="--dumps --xml failed"):
            sislc.dumps_xml('<root><x type="int">abc</x></root>')

    def test_invalid_bool_value(self, sislc):
        """Invalid boolean value produces an error."""
        with pytest.raises(RuntimeError, match="--dumps --xml failed"):
            sislc.dumps_xml('<root><x type="bool">yes</x></root>')

    def test_int_trailing_garbage(self, sislc):
        """Integer with trailing non-numeric text produces an error."""
        with pytest.raises(RuntimeError, match="--dumps --xml failed"):
            sislc.dumps_xml('<root><x type="int">42abc</x></root>')

    def test_float_trailing_garbage(self, sislc):
        """Float with trailing non-numeric text produces an error."""
        with pytest.raises(RuntimeError, match="--dumps --xml failed"):
            sislc.dumps_xml('<root><x type="float">3.14xyz</x></root>')


class TestXmlSpecialCharacters:
    """Test XML handling of special characters in string values."""

    def test_ampersand_roundtrip(self, sislc):
        """String containing & survives XML round-trip."""
        obj = {"text": "a & b"}
        sisl_str = sislc.dumps(obj)
        xml_out = sislc.loads_xml(sisl_str)
        sisl_str2 = sislc.dumps_xml(xml_out)
        result = sislc.loads(sisl_str2)
        assert result == obj

    def test_angle_brackets_roundtrip(self, sislc):
        """String containing < and > survives XML round-trip."""
        obj = {"text": "a < b > c"}
        sisl_str = sislc.dumps(obj)
        xml_out = sislc.loads_xml(sisl_str)
        sisl_str2 = sislc.dumps_xml(xml_out)
        result = sislc.loads(sisl_str2)
        assert result == obj

    def test_quotes_roundtrip(self, sislc):
        """String containing quotes survives XML round-trip."""
        obj = {"text": 'he said "hello"'}
        sisl_str = sislc.dumps(obj)
        xml_out = sislc.loads_xml(sisl_str)
        sisl_str2 = sislc.dumps_xml(xml_out)
        result = sislc.loads(sisl_str2)
        assert result == obj

    def test_mixed_special_chars(self, sislc):
        """String with mixed XML-special characters."""
        obj = {"formula": "x < 10 && y > 5"}
        sisl_str = sislc.dumps(obj)
        xml_out = sislc.loads_xml(sisl_str)
        sisl_str2 = sislc.dumps_xml(xml_out)
        result = sislc.loads(sisl_str2)
        assert result == obj


class TestXmlEmptyStructures:
    """Test XML with empty objects and lists."""

    def test_empty_object(self, sislc):
        """Empty nested object round-trips through XML."""
        obj = {"data": {}}
        sisl_str = sislc.dumps(obj)
        xml_out = sislc.loads_xml(sisl_str)
        sisl_str2 = sislc.dumps_xml(xml_out)
        result = sislc.loads(sisl_str2)
        assert result == obj

    def test_empty_list(self, sislc):
        """Empty list round-trips through XML."""
        obj = {"items": []}
        sisl_str = sislc.dumps(obj)
        xml_out = sislc.loads_xml(sisl_str)
        sisl_str2 = sislc.dumps_xml(xml_out)
        result = sislc.loads(sisl_str2)
        assert result == obj

    def test_empty_top_level(self, sislc):
        """Empty top-level object produces valid XML."""
        sisl_str = sislc.dumps({})
        xml_out = sislc.loads_xml(sisl_str)
        root = ET.fromstring(xml_out)
        assert root.tag == "root"
        assert len(list(root)) == 0


class TestXmlDeepNesting:
    """Test XML with deeply nested structures."""

    def test_three_level_nesting(self, sislc):
        """Three levels of object nesting round-trips."""
        obj = {"a": {"b": {"c": "deep"}}}
        sisl_str = sislc.dumps(obj)
        xml_out = sislc.loads_xml(sisl_str)
        sisl_str2 = sislc.dumps_xml(xml_out)
        result = sislc.loads(sisl_str2)
        assert result == obj

    def test_nested_list_in_object(self, sislc):
        """List inside object inside list round-trips."""
        obj = {"data": [{"items": [1, 2]}, {"items": [3, 4]}]}
        sisl_str = sislc.dumps(obj)
        xml_out = sislc.loads_xml(sisl_str)
        sisl_str2 = sislc.dumps_xml(xml_out)
        result = sislc.loads(sisl_str2)
        assert result == obj

    def test_five_level_nesting(self, sislc):
        """Five levels of nesting round-trips."""
        obj = {"l1": {"l2": {"l3": {"l4": {"l5": "value"}}}}}
        sisl_str = sislc.dumps(obj)
        xml_out = sislc.loads_xml(sisl_str)
        sisl_str2 = sislc.dumps_xml(xml_out)
        result = sislc.loads(sisl_str2)
        assert result == obj
