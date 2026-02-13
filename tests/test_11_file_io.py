"""
Test 11: File Input/Output
===========================
Tests for --input and --output file path arguments.
"""

import json
import os
import tempfile
import pytest


class TestFileInput:
    """Test reading input from a file with --input."""

    def test_dumps_from_json_file(self, sislc):
        """--dumps --input reads JSON from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"name": "Alice", "age": 30}, f)
            f.flush()
            rc, stdout, stderr = sislc.run_with_files(["--dumps"], input_file=f.name)
        os.unlink(f.name)
        assert rc == 0
        result = sislc.loads(stdout.strip())
        assert result == {"name": "Alice", "age": 30}

    def test_dumps_from_xml_file(self, sislc):
        """--dumps --xml --input reads XML from file."""
        xml_content = '<root><name type="str">Bob</name></root>'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            rc, stdout, stderr = sislc.run_with_files(
                ["--dumps", "--xml"], input_file=f.name
            )
        os.unlink(f.name)
        assert rc == 0
        result = sislc.loads(stdout.strip())
        assert result == {"name": "Bob"}

    def test_loads_from_sisl_file(self, sislc):
        """--loads --input reads SISL from file."""
        sisl_content = '{name: !str "Alice", age: !int "30"}'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sisl", delete=False) as f:
            f.write(sisl_content)
            f.flush()
            rc, stdout, stderr = sislc.run_with_files(["--loads"], input_file=f.name)
        os.unlink(f.name)
        assert rc == 0
        result = json.loads(stdout.strip())
        assert result == {"name": "Alice", "age": 30}

    def test_input_file_not_found(self, sislc):
        """--input with nonexistent file produces an error."""
        rc, stdout, stderr = sislc.run_with_files(
            ["--dumps"], input_file="/tmp/nonexistent_sislc_test_file.json"
        )
        assert rc != 0
        assert "Cannot open input file" in stderr


class TestFileOutput:
    """Test writing output to a file with --output."""

    def test_dumps_to_file(self, sislc):
        """--dumps --output writes SISL to file."""
        with tempfile.NamedTemporaryFile(suffix=".sisl", delete=False) as f:
            out_path = f.name
        try:
            rc, stdout, stderr = sislc.run_with_files(
                ["--dumps"], output_file=out_path,
                stdin_data='{"name": "Alice"}'
            )
            assert rc == 0
            assert stdout == ""  # stdout should be empty
            with open(out_path) as f:
                content = f.read().strip()
            result = sislc.loads(content)
            assert result == {"name": "Alice"}
        finally:
            os.unlink(out_path)

    def test_loads_to_json_file(self, sislc):
        """--loads --output writes JSON to file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            out_path = f.name
        try:
            rc, stdout, stderr = sislc.run_with_files(
                ["--loads"], output_file=out_path,
                stdin_data='{name: !str "Alice", age: !int "30"}'
            )
            assert rc == 0
            assert stdout == ""
            with open(out_path) as f:
                result = json.load(f)
            assert result == {"name": "Alice", "age": 30}
        finally:
            os.unlink(out_path)

    def test_loads_to_xml_file(self, sislc):
        """--loads --xml --output writes XML to file."""
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
            out_path = f.name
        try:
            rc, stdout, stderr = sislc.run_with_files(
                ["--loads", "--xml"], output_file=out_path,
                stdin_data='{name: !str "Alice"}'
            )
            assert rc == 0
            assert stdout == ""
            with open(out_path) as f:
                content = f.read()
            assert "<?xml" in content
            assert '<name type="str">Alice</name>' in content
        finally:
            os.unlink(out_path)

    def test_output_file_bad_path(self, sislc):
        """--output with unwritable path produces an error."""
        rc, stdout, stderr = sislc.run_with_files(
            ["--dumps"], output_file="/nonexistent_dir/out.sisl",
            stdin_data='{"x": 1}'
        )
        assert rc != 0
        assert "Cannot open output file" in stderr

    def test_output_file_not_created_on_failure(self, sislc):
        """--output file is not left behind when processing fails."""
        with tempfile.NamedTemporaryFile(suffix=".sisl", delete=False) as f:
            out_path = f.name
        # Remove so we can check if it gets created
        os.unlink(out_path)
        try:
            rc, stdout, stderr = sislc.run_with_files(
                ["--dumps"], output_file=out_path,
                stdin_data="this is not valid json"
            )
            assert rc != 0
            # Output file should not exist (temp was cleaned up on failure)
            assert not os.path.exists(out_path)
        finally:
            if os.path.exists(out_path):
                os.unlink(out_path)


class TestFileInputAndOutput:
    """Test using --input and --output together."""

    def test_dumps_file_to_file(self, sislc):
        """--dumps --input FILE --output FILE converts file to file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as inf:
            json.dump({"city": "London", "pop": 9000000}, inf)
            in_path = inf.name
        with tempfile.NamedTemporaryFile(suffix=".sisl", delete=False) as outf:
            out_path = outf.name
        try:
            rc, stdout, stderr = sislc.run_with_files(
                ["--dumps"], input_file=in_path, output_file=out_path
            )
            assert rc == 0
            assert stdout == ""
            with open(out_path) as f:
                sisl_content = f.read().strip()
            result = sislc.loads(sisl_content)
            assert result == {"city": "London", "pop": 9000000}
        finally:
            os.unlink(in_path)
            os.unlink(out_path)

    def test_loads_file_to_file(self, sislc):
        """--loads --input FILE --output FILE converts file to file."""
        sisl_content = '{city: !str "London", pop: !int "9000000"}'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sisl", delete=False) as inf:
            inf.write(sisl_content)
            in_path = inf.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as outf:
            out_path = outf.name
        try:
            rc, stdout, stderr = sislc.run_with_files(
                ["--loads"], input_file=in_path, output_file=out_path
            )
            assert rc == 0
            with open(out_path) as f:
                result = json.load(f)
            assert result == {"city": "London", "pop": 9000000}
        finally:
            os.unlink(in_path)
            os.unlink(out_path)

    def test_xml_file_to_sisl_file(self, sislc):
        """--dumps --xml --input XML --output SISL."""
        xml_content = '<root><x type="int">42</x></root>'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as inf:
            inf.write(xml_content)
            in_path = inf.name
        with tempfile.NamedTemporaryFile(suffix=".sisl", delete=False) as outf:
            out_path = outf.name
        try:
            rc, stdout, stderr = sislc.run_with_files(
                ["--dumps", "--xml"], input_file=in_path, output_file=out_path
            )
            assert rc == 0
            with open(out_path) as f:
                sisl_content = f.read().strip()
            result = sislc.loads(sisl_content)
            assert result == {"x": 42}
        finally:
            os.unlink(in_path)
            os.unlink(out_path)

    def test_sisl_file_to_xml_file(self, sislc):
        """--loads --xml --input SISL --output XML."""
        sisl_content = '{x: !int "42"}'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sisl", delete=False) as inf:
            inf.write(sisl_content)
            in_path = inf.name
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as outf:
            out_path = outf.name
        try:
            rc, stdout, stderr = sislc.run_with_files(
                ["--loads", "--xml"], input_file=in_path, output_file=out_path
            )
            assert rc == 0
            with open(out_path) as f:
                content = f.read()
            assert "<?xml" in content
            assert '<x type="int">42</x>' in content
        finally:
            os.unlink(in_path)
            os.unlink(out_path)

    def test_split_with_file_output(self, sislc):
        """--dumps --max-length --input FILE --output FILE writes split fragments."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as inf:
            json.dump({"a": "value1", "b": "value2", "c": "value3"}, inf)
            in_path = inf.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as outf:
            out_path = outf.name
        try:
            rc, stdout, stderr = sislc.run_with_files(
                ["--dumps", "--max-length", "50"],
                input_file=in_path, output_file=out_path
            )
            assert rc == 0
            with open(out_path) as f:
                content = f.read().strip()
            fragments = json.loads(content)
            assert isinstance(fragments, list)
            assert len(fragments) >= 2
            merged = sislc.loads(fragments)
            assert merged["a"] == "value1"
            assert merged["b"] == "value2"
            assert merged["c"] == "value3"
        finally:
            os.unlink(in_path)
            os.unlink(out_path)


class TestFileArgErrors:
    """Test argument validation for --input and --output."""

    def test_input_missing_value(self, sislc):
        """--input without a path produces an error."""
        # Pass --input as a bare flag (no value) via run_with_files args
        rc, stdout, stderr = sislc.run_with_files(["--dumps", "--input"])
        assert rc != 0
        assert "requires a file path" in stderr

    def test_output_missing_value(self, sislc):
        """--output without a path produces an error."""
        rc, stdout, stderr = sislc.run_with_files(
            ["--dumps", "--output"], stdin_data='{"x": 1}'
        )
        assert rc != 0
        assert "requires a file path" in stderr
