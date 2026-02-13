"""Pytest configuration and shared fixtures for SISL interoperability tests."""

import subprocess
import json
import os
import tempfile
import pytest

# Path to sislc binary
SISLC_PATH = os.path.join(os.path.dirname(__file__), "..", "build", "sislc")


@pytest.fixture
def sislc():
    """Fixture providing sislc helper functions."""
    class SislcHelper:
        @staticmethod
        def dumps(json_obj, max_length=None):
            """Convert JSON to SISL using sislc."""
            cmd = [SISLC_PATH, "--dumps"]
            if max_length:
                cmd.extend(["--max-length", str(max_length)])
            result = subprocess.run(
                cmd,
                input=json.dumps(json_obj),
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"sislc --dumps failed: {result.stderr}")
            output = result.stdout.strip()
            # If it's a JSON array (split result), parse it
            if max_length and output.startswith("["):
                return json.loads(output)
            return output

        @staticmethod
        def loads(sisl_input):
            """Convert SISL to JSON using sislc."""
            # If input is a list, convert to JSON array string
            if isinstance(sisl_input, list):
                sisl_input = json.dumps(sisl_input)
            result = subprocess.run(
                [SISLC_PATH, "--loads"],
                input=sisl_input,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"sislc --loads failed: {result.stderr}")
            return json.loads(result.stdout.strip())

        @staticmethod
        def loads_raw(sisl_input):
            """Convert SISL to raw JSON string using sislc (no Python parse)."""
            if isinstance(sisl_input, list):
                sisl_input = json.dumps(sisl_input)
            result = subprocess.run(
                [SISLC_PATH, "--loads"],
                input=sisl_input,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"sislc --loads failed: {result.stderr}")
            return result.stdout.strip()

        @staticmethod
        def dumps_raw(json_str, max_length=None):
            """Convert raw JSON string to SISL using sislc."""
            cmd = [SISLC_PATH, "--dumps"]
            if max_length:
                cmd.extend(["--max-length", str(max_length)])
            result = subprocess.run(
                cmd,
                input=json_str,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"sislc --dumps failed: {result.stderr}")
            return result.stdout.strip()

        @staticmethod
        def dumps_xml(xml_str, max_length=None):
            """Convert XML string to SISL using sislc --dumps --xml."""
            cmd = [SISLC_PATH, "--dumps", "--xml"]
            if max_length:
                cmd.extend(["--max-length", str(max_length)])
            result = subprocess.run(
                cmd,
                input=xml_str,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"sislc --dumps --xml failed: {result.stderr}")
            output = result.stdout.strip()
            if max_length and output.startswith("["):
                return json.loads(output)
            return output

        @staticmethod
        def loads_xml(sisl_input):
            """Convert SISL to XML using sislc --loads --xml."""
            if isinstance(sisl_input, list):
                sisl_input = json.dumps(sisl_input)
            result = subprocess.run(
                [SISLC_PATH, "--loads", "--xml"],
                input=sisl_input,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"sislc --loads --xml failed: {result.stderr}")
            return result.stdout

        @staticmethod
        def run_with_files(args, input_file=None, output_file=None, stdin_data=None):
            """Run sislc with --input/--output file arguments.

            Returns (returncode, stdout, stderr) tuple.
            """
            cmd = [SISLC_PATH] + args
            if input_file:
                cmd.extend(["--input", input_file])
            if output_file:
                cmd.extend(["--output", output_file])
            result = subprocess.run(
                cmd,
                input=stdin_data,
                capture_output=True,
                text=True
            )
            return result.returncode, result.stdout, result.stderr

    return SislcHelper()
