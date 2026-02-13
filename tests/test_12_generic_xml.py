"""
Test 12: Generic XML Mode
==========================
Tests for arbitrary (non-typed) XML round-tripping through the generic XML codec.

The generic mode activates automatically when XML input lacks the typed format
(<root> + type attributes). It preserves tag names, attributes, text content,
and element hierarchy using a JSON representation with _tag, _attrs, _text,
and _children keys.
"""

import json
import os
import tempfile
import pytest
import xml.etree.ElementTree as ET


class TestGenericXmlDetection:
    """Test auto-detection routing between typed and generic modes."""

    def test_typed_xml_still_works(self, sislc):
        """Typed XML with <root> and type attrs uses the typed path."""
        xml_in = '<root><name type="str">Alice</name></root>'
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        # Typed mode produces flat key-value, not _root wrapper
        assert result == {"name": "Alice"}

    def test_non_root_element_triggers_generic(self, sislc):
        """XML without <root> element triggers generic mode."""
        xml_in = "<data><item>hello</item></data>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert "_root" in result
        assert result["_root"]["_tag"] == "data"

    def test_root_without_type_attrs_triggers_generic(self, sislc):
        """<root> element whose children lack type attrs triggers generic mode."""
        xml_in = "<root><name>Alice</name></root>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert "_root" in result
        assert result["_root"]["_tag"] == "root"

    def test_generic_json_routes_to_generic_xml(self, sislc):
        """JSON with _root key produces generic XML output."""
        obj = {"_root": {"_tag": "doc", "_text": "hello"}}
        sisl_str = sislc.dumps(obj)
        xml_out = sislc.loads_xml(sisl_str)
        root = ET.fromstring(xml_out)
        assert root.tag == "doc"
        assert root.text == "hello"

    def test_json_without_root_key_routes_to_typed(self, sislc):
        """JSON without _root key produces typed XML output."""
        obj = {"name": "Alice"}
        sisl_str = sislc.dumps(obj)
        xml_out = sislc.loads_xml(sisl_str)
        root = ET.fromstring(xml_out)
        assert root.tag == "root"
        assert root.find("name").get("type") == "str"


class TestGenericXmlBasicStructures:
    """Test basic element parsing and reconstruction."""

    def test_single_text_element(self, sislc):
        """Single element with text content."""
        xml_in = "<greeting>Hello World</greeting>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert result["_root"]["_tag"] == "greeting"
        assert result["_root"]["_text"] == "Hello World"

    def test_empty_element(self, sislc):
        """Empty self-closing element has no _text or _children."""
        xml_in = "<empty/>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        root = result["_root"]
        assert root["_tag"] == "empty"
        assert "_text" not in root
        assert "_children" not in root

    def test_element_with_single_child(self, sislc):
        """Element with one child element."""
        xml_in = "<parent><child>text</child></parent>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        root = result["_root"]
        assert root["_tag"] == "parent"
        assert len(root["_children"]) == 1
        assert root["_children"][0]["_tag"] == "child"
        assert root["_children"][0]["_text"] == "text"

    def test_element_with_multiple_children(self, sislc):
        """Element with several child elements."""
        xml_in = "<list><a>1</a><b>2</b><c>3</c></list>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        children = result["_root"]["_children"]
        assert len(children) == 3
        assert children[0]["_tag"] == "a"
        assert children[1]["_tag"] == "b"
        assert children[2]["_tag"] == "c"

    def test_element_with_attributes(self, sislc):
        """Element attributes are captured in _attrs."""
        xml_in = '<item id="42" status="active">content</item>'
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        root = result["_root"]
        assert root["_attrs"]["id"] == "42"
        assert root["_attrs"]["status"] == "active"
        assert root["_text"] == "content"

    def test_empty_element_with_attributes(self, sislc):
        """Empty element with attributes only."""
        xml_in = '<br class="clear"/>'
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        root = result["_root"]
        assert root["_tag"] == "br"
        assert root["_attrs"]["class"] == "clear"
        assert "_text" not in root
        assert "_children" not in root


class TestGenericXmlDeclaration:
    """Test XML declaration preservation."""

    def test_declaration_preserved(self, sislc):
        """XML declaration attributes are captured in _decl."""
        xml_in = '<?xml version="1.0" encoding="UTF-8"?><doc/>'
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert result["_decl"]["version"] == "1.0"
        assert result["_decl"]["encoding"] == "UTF-8"

    def test_declaration_with_standalone(self, sislc):
        """standalone attribute in declaration is preserved."""
        xml_in = '<?xml version="1.0" encoding="utf-8" standalone="yes"?><doc/>'
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert result["_decl"]["standalone"] == "yes"

    def test_declaration_round_trips(self, sislc):
        """Declaration attributes survive a full round-trip."""
        xml_in = '<?xml version="1.0" encoding="utf-8" standalone="yes"?><doc/>'
        sisl_out = sislc.dumps_xml(xml_in)
        xml_out = sislc.loads_xml(sisl_out)
        assert 'version="1.0"' in xml_out
        assert 'encoding="utf-8"' in xml_out
        assert 'standalone="yes"' in xml_out

    def test_no_declaration(self, sislc):
        """XML without a declaration omits _decl."""
        xml_in = "<doc/>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert "_decl" not in result


class TestGenericXmlDeepNesting:
    """Test deeply and complexly nested XML structures."""

    def test_five_levels_deep(self, sislc):
        """Five levels of nesting round-trips."""
        xml_in = "<a><b><c><d><e>deep</e></d></c></b></a>"
        sisl_out = sislc.dumps_xml(xml_in)
        xml_out = sislc.loads_xml(sisl_out)
        sisl_out2 = sislc.dumps_xml(xml_out)
        result = sislc.loads(sisl_out2)
        node = result["_root"]
        for tag in ["a", "b", "c", "d", "e"]:
            assert node["_tag"] == tag
            if tag == "e":
                assert node["_text"] == "deep"
            else:
                node = node["_children"][0]

    def test_wide_and_deep(self, sislc):
        """Element with both breadth and depth."""
        xml_in = """<tree>
            <branch1><leaf>A</leaf><leaf>B</leaf></branch1>
            <branch2><twig><leaf>C</leaf></twig></branch2>
            <branch3/>
        </tree>"""
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        children = result["_root"]["_children"]
        assert len(children) == 3
        assert children[0]["_tag"] == "branch1"
        assert len(children[0]["_children"]) == 2
        assert children[1]["_children"][0]["_tag"] == "twig"
        assert children[2]["_tag"] == "branch3"
        assert "_children" not in children[2]

    def test_repeated_same_name_siblings(self, sislc):
        """Multiple sibling elements with the same tag name."""
        xml_in = "<list><item>A</item><item>B</item><item>C</item><item>D</item></list>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        children = result["_root"]["_children"]
        assert len(children) == 4
        assert all(c["_tag"] == "item" for c in children)
        assert [c["_text"] for c in children] == ["A", "B", "C", "D"]

    def test_heterogeneous_siblings(self, sislc):
        """Siblings with different tag names and structures mixed together."""
        xml_in = """<record>
            <id>1</id>
            <name>Test</name>
            <tags><tag>a</tag><tag>b</tag></tags>
            <meta/>
            <value>42</value>
        </record>"""
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        children = result["_root"]["_children"]
        assert len(children) == 5
        tags = [c["_tag"] for c in children]
        assert tags == ["id", "name", "tags", "meta", "value"]
        # meta is empty
        assert "_text" not in children[3]
        assert "_children" not in children[3]
        # tags has children
        assert len(children[2]["_children"]) == 2


class TestGenericXmlNamespaces:
    """Test namespace handling in generic mode."""

    def test_xmlns_attribute_preserved(self, sislc):
        """xmlns attribute is treated as a regular attribute."""
        xml_in = '<doc xmlns="http://example.com"><item>x</item></doc>'
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert result["_root"]["_attrs"]["xmlns"] == "http://example.com"

    def test_prefixed_xmlns_produces_sisl(self, sislc):
        """xmlns:prefix declarations are encoded to SISL (XML-to-SISL step works)."""
        xml_in = '<doc xmlns:ns="http://example.com"><ns:item>x</ns:item></doc>'
        sisl_out = sislc.dumps_xml(xml_in)
        # The encoder produces SISL containing the namespace data
        assert "xmlns:ns" in sisl_out
        assert "http://example.com" in sisl_out
        assert "ns:item" in sisl_out

    def test_prefixed_xmlns_sisl_round_trip_fails(self, sislc):
        """Colons in attribute names (xmlns:prefix) break SISL round-trip.

        SISL uses ':' as its key-value separator, so JSON keys containing
        colons cannot survive a SISL encode-decode cycle. This affects
        xmlns:prefix declarations and any attribute with a colon in its name.
        """
        xml_in = '<doc xmlns:ns="http://example.com"><ns:item>x</ns:item></doc>'
        sisl_out = sislc.dumps_xml(xml_in)
        # Re-loading the SISL string fails because 'xmlns:ns' clashes with
        # SISL's key: !type "value" syntax
        with pytest.raises(RuntimeError, match="--loads failed"):
            sislc.loads(sisl_out)

    def test_multiple_prefixed_namespaces_break_sisl(self, sislc):
        """Multiple xmlns:prefix declarations also break SISL round-trip."""
        xml_in = (
            '<root xmlns:a="http://a.example.com" '
            'xmlns:b="http://b.example.com">'
            '<a:item>X</a:item><b:item>Y</b:item></root>'
        )
        sisl_out = sislc.dumps_xml(xml_in)
        with pytest.raises(RuntimeError, match="--loads failed"):
            sislc.loads(sisl_out)

    def test_non_prefixed_namespace_round_trips(self, sislc):
        """Non-prefixed xmlns (no colon) round-trips fine through SISL."""
        xml_in = '<doc xmlns="http://example.com"><item>x</item></doc>'
        sisl_out = sislc.dumps_xml(xml_in)
        xml_out = sislc.loads_xml(sisl_out)
        # Check the raw XML string since Python's ET interprets xmlns specially
        assert 'xmlns="http://example.com"' in xml_out


class TestGenericXmlSpecialContent:
    """Test special characters, CDATA, and Unicode content."""

    def test_ampersand_in_text(self, sislc):
        """Ampersand in text content round-trips."""
        xml_in = "<msg>rock &amp; roll</msg>"
        sisl_out = sislc.dumps_xml(xml_in)
        xml_out = sislc.loads_xml(sisl_out)
        sisl_out2 = sislc.dumps_xml(xml_out)
        result = sislc.loads(sisl_out2)
        assert result["_root"]["_text"] == "rock & roll"

    def test_angle_brackets_in_text(self, sislc):
        """Angle brackets in text content round-trip."""
        xml_in = "<expr>x &lt; 10 &amp;&amp; y &gt; 5</expr>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert result["_root"]["_text"] == "x < 10 && y > 5"

    def test_quotes_in_attributes(self, sislc):
        """Escaped quotes in attribute values round-trip."""
        xml_in = '<rule match="name = &quot;test&quot;" />'
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert result["_root"]["_attrs"]["match"] == 'name = "test"'

    def test_special_chars_in_attributes(self, sislc):
        """Angle brackets and ampersands in attributes round-trip."""
        xml_in = '<rule expr="x &lt; 10 &amp;&amp; y &gt; 5" />'
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert result["_root"]["_attrs"]["expr"] == "x < 10 && y > 5"

    def test_unicode_text(self, sislc):
        """Unicode text content round-trips."""
        xml_in = '<?xml version="1.0" encoding="UTF-8"?><msg>你好世界 café ☕</msg>'
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert result["_root"]["_text"] == "你好世界 café ☕"

    def test_unicode_attributes(self, sislc):
        """Unicode attribute values round-trip."""
        xml_in = '<user name="Ñoño" city="Zürich"/>'
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert result["_root"]["_attrs"]["name"] == "Ñoño"
        assert result["_root"]["_attrs"]["city"] == "Zürich"

    def test_cdata_normalized_to_text(self, sislc):
        """CDATA sections are normalized to plain text content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write("<doc><![CDATA[raw content here]]></doc>")
            f.flush()
            try:
                rc, stdout, _ = sislc.run_with_files(["--dumps", "--xml"], input_file=f.name)
                assert rc == 0
                loaded = sislc.loads(stdout.strip())
                assert loaded["_root"]["_text"] == "raw content here"
            finally:
                os.unlink(f.name)


class TestGenericXmlLimitations:
    """Test known limitations of the generic XML codec.

    These tests document and verify the expected behavior for XML features
    that are not fully preserved through a round-trip.
    """

    def test_mixed_content_loses_interleaved_text(self, sislc):
        """Mixed content: interleaved text nodes between child elements are dropped."""
        xml_in = "<p>Hello <b>bold</b> and <i>italic</i> text</p>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        root = result["_root"]
        # Only child elements remain; "Hello ", " and ", " text" are lost
        assert "_text" not in root
        assert len(root["_children"]) == 2
        assert root["_children"][0]["_tag"] == "b"
        assert root["_children"][1]["_tag"] == "i"

    def test_comments_stripped(self, sislc):
        """XML comments are silently stripped during parsing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write("<doc><!-- important comment --><item>text</item></doc>")
            f.flush()
            try:
                rc, stdout, _ = sislc.run_with_files(["--dumps", "--xml"], input_file=f.name)
                assert rc == 0
                loaded = sislc.loads(stdout.strip())
                children = loaded["_root"]["_children"]
                # Only the <item> element survives; comment is gone
                assert len(children) == 1
                assert children[0]["_tag"] == "item"
            finally:
                os.unlink(f.name)

    def test_processing_instructions_stripped(self, sislc):
        """Processing instructions (other than <?xml?>) are stripped."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(
                '<?xml version="1.0"?>'
                '<?xml-stylesheet type="text/xsl" href="style.xsl"?>'
                "<doc><item>text</item></doc>"
            )
            f.flush()
            try:
                rc, stdout, _ = sislc.run_with_files(["--dumps", "--xml"], input_file=f.name)
                assert rc == 0
                loaded = sislc.loads(stdout.strip())
                # Declaration is preserved, PI is not
                assert "_decl" in loaded
                assert loaded["_root"]["_tag"] == "doc"
            finally:
                os.unlink(f.name)

    def test_output_uses_tabs_for_indent(self, sislc):
        """Generic XML output uses tab indentation."""
        xml_in = "<doc><item>text</item></doc>"
        sisl_out = sislc.dumps_xml(xml_in)
        xml_out = sislc.loads_xml(sisl_out)
        assert "\t<item>" in xml_out

    def test_output_uses_double_quotes(self, sislc):
        """Generic XML output always uses double quotes for attributes."""
        xml_in = "<doc><item key=\"val\">text</item></doc>"
        sisl_out = sislc.dumps_xml(xml_in)
        xml_out = sislc.loads_xml(sisl_out)
        assert 'key="val"' in xml_out

    def test_empty_elements_self_close(self, sislc):
        """Empty elements are output as self-closing tags."""
        xml_in = "<doc><br/></doc>"
        sisl_out = sislc.dumps_xml(xml_in)
        xml_out = sislc.loads_xml(sisl_out)
        assert "<br />" in xml_out


class TestGenericXmlRoundTrips:
    """Test full round-trip fidelity for complex XML documents."""

    def test_catalog_round_trip(self, sislc):
        """Complex catalog document with attributes and nesting."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<catalog>
\t<book id="1" lang="en">
\t\t<title>The Great Gatsby</title>
\t\t<author>
\t\t\t<first>F. Scott</first>
\t\t\t<last>Fitzgerald</last>
\t\t</author>
\t\t<tags>
\t\t\t<tag>classic</tag>
\t\t\t<tag>fiction</tag>
\t\t</tags>
\t</book>
\t<book id="2" lang="fr">
\t\t<title>Le Petit Prince</title>
\t\t<author>
\t\t\t<first>Antoine</first>
\t\t\t<last>de Saint-Exupery</last>
\t\t</author>
\t\t<tags>
\t\t\t<tag>classic</tag>
\t\t\t<tag>children</tag>
\t\t</tags>
\t</book>
</catalog>
""")
            f.flush()
            try:
                # Round-trip: XML -> SISL -> XML -> SISL -> JSON
                rc1, sisl1, _ = sislc.run_with_files(
                    ["--dumps", "--xml"], input_file=f.name
                )
                assert rc1 == 0

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".sisl", delete=False
                ) as sf:
                    sf.write(sisl1)
                    sf.flush()
                    rc2, xml_out, _ = sislc.run_with_files(
                        ["--loads", "--xml"], input_file=sf.name
                    )
                    os.unlink(sf.name)
                assert rc2 == 0

                # Second round-trip must be stable
                sisl2 = sislc.dumps_xml(xml_out)
                xml_out2 = sislc.loads_xml(sisl2)
                assert xml_out == xml_out2
            finally:
                os.unlink(f.name)

    def test_second_round_trip_is_stable(self, sislc):
        """After first round-trip, subsequent ones produce identical output."""
        xml_in = """<?xml version="1.0"?>
<events>
  <event type="login" time="2023-01-01T00:00:00Z">
    <user id="1">admin</user>
    <source ip="192.168.1.1" port="443"/>
  </event>
  <event type="logout" time="2023-01-01T01:00:00Z">
    <user id="1">admin</user>
  </event>
</events>"""
        # First trip
        sisl1 = sislc.dumps_xml(xml_in)
        xml1 = sislc.loads_xml(sisl1)
        # Second trip
        sisl2 = sislc.dumps_xml(xml1)
        xml2 = sislc.loads_xml(sisl2)
        assert xml1 == xml2

    def test_windows_event_log_structure(self, sislc):
        """Windows Event Log-style XML round-trips structurally."""
        xml_in = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<Events>
\t<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
\t\t<System>
\t\t\t<Provider Name="nssm" />
\t\t\t<EventID Qualifiers="16384">1008</EventID>
\t\t\t<Level>4</Level>
\t\t\t<Task>0</Task>
\t\t\t<TimeCreated SystemTime="2023-06-22T12:38:32Z" />
\t\t\t<EventRecordID>1301550</EventRecordID>
\t\t\t<Channel>Application</Channel>
\t\t\t<Security />
\t\t</System>
\t\t<EventData>
\t\t\t<Data>srv.exe</Data>
\t\t\t<Data>4Secure Directory Sync</Data>
\t\t</EventData>
\t</Event>
</Events>
"""
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)

        # Verify structure
        root = result["_root"]
        assert root["_tag"] == "Events"
        event = root["_children"][0]
        assert event["_tag"] == "Event"
        assert event["_attrs"]["xmlns"] == "http://schemas.microsoft.com/win/2004/08/events/event"

        system = event["_children"][0]
        assert system["_tag"] == "System"
        provider = system["_children"][0]
        assert provider["_attrs"]["Name"] == "nssm"

        event_data = event["_children"][1]
        assert event_data["_tag"] == "EventData"
        assert len(event_data["_children"]) == 2

        # Round-trip stability
        xml_out = sislc.loads_xml(sisl_out)
        sisl_out2 = sislc.dumps_xml(xml_out)
        xml_out2 = sislc.loads_xml(sisl_out2)
        assert xml_out == xml_out2

    def test_many_attributes(self, sislc):
        """Element with many attributes round-trips."""
        attrs = " ".join(f'attr{i}="val{i}"' for i in range(20))
        xml_in = f"<item {attrs}>content</item>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        for i in range(20):
            assert result["_root"]["_attrs"][f"attr{i}"] == f"val{i}"

    def test_deeply_nested_with_attributes(self, sislc):
        """Deep nesting where every level has attributes."""
        xml_in = (
            '<a id="1"><b id="2"><c id="3"><d id="4">'
            '<e id="5">leaf</e></d></c></b></a>'
        )
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        node = result["_root"]
        for i, tag in enumerate(["a", "b", "c", "d", "e"], 1):
            assert node["_tag"] == tag
            assert node["_attrs"]["id"] == str(i)
            if tag != "e":
                node = node["_children"][0]
            else:
                assert node["_text"] == "leaf"


class TestGenericXmlWithSplitting:
    """Test generic XML combined with --max-length splitting.

    Splitting is largely ineffective with generic XML because the entire
    document nests under a single _root key. The splitter operates at the
    top-level key boundary (_decl, _root) and cannot break apart the deeply
    nested _root subtree.
    """

    def test_generic_xml_no_split_when_fits(self, sislc):
        """Small generic XML within max-length produces a single string."""
        xml_in = "<doc><item>x</item></doc>"
        result = sislc.dumps_xml(xml_in, max_length=5000)
        assert isinstance(result, str)
        loaded = sislc.loads(result)
        assert loaded["_root"]["_tag"] == "doc"
        assert loaded["_root"]["_children"][0]["_text"] == "x"


class TestGenericXmlEdgeCases:
    """Test unusual but valid XML edge cases."""

    def test_single_empty_root(self, sislc):
        """A single empty root element."""
        xml_in = "<empty/>"
        sisl_out = sislc.dumps_xml(xml_in)
        xml_out = sislc.loads_xml(sisl_out)
        sisl_out2 = sislc.dumps_xml(xml_out)
        xml_out2 = sislc.loads_xml(sisl_out2)
        assert xml_out == xml_out2

    def test_hyphenated_tag_names(self, sislc):
        """Tag names with hyphens."""
        xml_in = "<my-root><my-item>text</my-item></my-root>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert result["_root"]["_tag"] == "my-root"
        assert result["_root"]["_children"][0]["_tag"] == "my-item"

    def test_dotted_tag_names(self, sislc):
        """Tag names with dots."""
        xml_in = "<com.example.root><com.example.item>text</com.example.item></com.example.root>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert result["_root"]["_tag"] == "com.example.root"

    def test_underscored_tag_names(self, sislc):
        """Tag names with underscores."""
        xml_in = "<_root><__item>text</__item></_root>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert result["_root"]["_tag"] == "_root"
        assert result["_root"]["_children"][0]["_tag"] == "__item"

    def test_numeric_text_stays_string(self, sislc):
        """Numeric text content stays as a string (not coerced to number)."""
        xml_in = "<val>42</val>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        assert result["_root"]["_text"] == "42"
        assert isinstance(result["_root"]["_text"], str)

    def test_whitespace_only_text_is_dropped(self, sislc):
        """Elements with only whitespace text are treated as empty.

        pugixml's default parse mode normalizes whitespace-only text content,
        resulting in an empty string which the codec treats as no text.
        """
        xml_in = "<doc><item>   </item></doc>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        child = result["_root"]["_children"][0]
        assert "_text" not in child

    def test_long_text_content(self, sislc):
        """Very long text content survives round-trip."""
        long_text = "A" * 10000
        xml_in = f"<doc>{long_text}</doc>"
        sisl_out = sislc.dumps_xml(xml_in)
        xml_out = sislc.loads_xml(sisl_out)
        sisl_out2 = sislc.dumps_xml(xml_out)
        result = sislc.loads(sisl_out2)
        assert result["_root"]["_text"] == long_text

    def test_many_siblings(self, sislc):
        """Large number of sibling elements."""
        items = "".join(f"<item>{i}</item>" for i in range(200))
        xml_in = f"<list>{items}</list>"
        sisl_out = sislc.dumps_xml(xml_in)
        result = sislc.loads(sisl_out)
        children = result["_root"]["_children"]
        assert len(children) == 200
        assert children[0]["_text"] == "0"
        assert children[199]["_text"] == "199"

    def test_attribute_order_preserved(self, sislc):
        """Attribute order is preserved through round-trip."""
        xml_in = '<item z="3" a="1" m="2"/>'
        sisl_out = sislc.dumps_xml(xml_in)
        xml_out = sislc.loads_xml(sisl_out)
        # Check that attributes appear in the output
        root = ET.fromstring(xml_out)
        assert root.get("z") == "3"
        assert root.get("a") == "1"
        assert root.get("m") == "2"
