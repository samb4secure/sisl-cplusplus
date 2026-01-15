"""
Test 06: Complex Structures
===========================
Tests for complex, real-world-like data structures combining multiple
nesting levels, types, and features.
"""

import pytest
import pysisl


class TestUserData:
    """User profile-like data structures."""

    def test_simple_user(self, sislc):
        """Simple user profile."""
        obj = {
            "id": 12345,
            "username": "johndoe",
            "email": "john@example.com",
            "active": True
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_user_with_address(self, sislc):
        """User with nested address."""
        obj = {
            "name": "Alice Smith",
            "address": {
                "street": "123 Main St",
                "city": "Boston",
                "state": "MA",
                "zip": "02101"
            }
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_user_with_tags(self, sislc):
        """User with array of tags."""
        obj = {
            "username": "developer",
            "tags": ["python", "javascript", "rust"],
            "level": 5
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_user_with_preferences(self, sislc):
        """User with nested preferences object."""
        obj = {
            "user": "testuser",
            "preferences": {
                "theme": "dark",
                "notifications": {
                    "email": True,
                    "push": False,
                    "sms": False
                },
                "language": "en"
            }
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj


class TestAPIResponse:
    """API response-like structures."""

    def test_paginated_response(self, sislc):
        """Paginated API response."""
        obj = {
            "data": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"},
                {"id": 3, "name": "Item 3"}
            ],
            "pagination": {
                "page": 1,
                "per_page": 10,
                "total": 100,
                "total_pages": 10
            }
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_error_response(self, sislc):
        """API error response."""
        obj = {
            "error": {
                "code": 404,
                "message": "Resource not found",
                "details": {
                    "resource_type": "user",
                    "resource_id": "abc123"
                }
            },
            "success": False
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_nested_array_response(self, sislc):
        """Response with nested arrays."""
        obj = {
            "matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            "dimensions": {"rows": 3, "cols": 3}
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj


class TestConfigurationData:
    """Configuration-like structures."""

    def test_app_config(self, sislc):
        """Application configuration."""
        obj = {
            "app": {
                "name": "MyApp",
                "version": "1.0.0",
                "debug": False
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "mydb"
            },
            "features": ["auth", "logging", "caching"]
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_nested_config(self, sislc):
        """Deeply nested configuration."""
        obj = {
            "server": {
                "http": {
                    "host": "0.0.0.0",
                    "port": 8080,
                    "ssl": {
                        "enabled": True,
                        "cert_path": "/etc/ssl/cert.pem",
                        "key_path": "/etc/ssl/key.pem"
                    }
                },
                "websocket": {
                    "enabled": True,
                    "path": "/ws"
                }
            }
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj


class TestDataRecords:
    """Data record structures."""

    def test_time_series_point(self, sislc):
        """Time series data point."""
        obj = {
            "timestamp": 1699900800,
            "metrics": {
                "cpu": 45.2,
                "memory": 67.8,
                "disk": 23.1
            },
            "tags": ["production", "web-server"]
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        # Compare with tolerance for floats
        assert cpp_result["timestamp"] == obj["timestamp"]
        assert cpp_result["tags"] == obj["tags"]
        for key in obj["metrics"]:
            assert abs(cpp_result["metrics"][key] - obj["metrics"][key]) < 0.01

    def test_event_log(self, sislc):
        """Event log entry."""
        obj = {
            "event_id": "evt_123456",
            "type": "user.login",
            "data": {
                "user_id": 42,
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0"
            },
            "metadata": {
                "processed": True,
                "retry_count": 0
            }
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj


class TestEdgeCases:
    """Complex edge cases."""

    def test_deeply_nested_mixed(self, sislc):
        """Deeply nested mixed structure."""
        obj = {
            "level1": {
                "level2": {
                    "level3": {
                        "array": [
                            {"key": "value"},
                            [1, 2, [3, 4, 5]],
                            "string",
                            42,
                            True,
                            None
                        ]
                    }
                }
            }
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_many_keys(self, sislc):
        """Object with many keys."""
        obj = {f"key_{i}": f"value_{i}" for i in range(50)}

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)
        assert cpp_result == obj

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result == obj

    def test_all_types_combined(self, sislc):
        """Object using all supported types."""
        obj = {
            "string": "text",
            "integer": 42,
            "negative_int": -17,
            "float_val": 3.14159,
            "bool_true": True,
            "bool_false": False,
            "null_val": None,
            "array": [1, "two", True, None],
            "nested_obj": {
                "inner_array": [1, 2, 3],
                "inner_string": "hello"
            }
        }

        py_sisl = pysisl.dumps(obj)
        cpp_result = sislc.loads(py_sisl)

        assert cpp_result["string"] == obj["string"]
        assert cpp_result["integer"] == obj["integer"]
        assert cpp_result["negative_int"] == obj["negative_int"]
        assert abs(cpp_result["float_val"] - obj["float_val"]) < 0.00001
        assert cpp_result["bool_true"] == obj["bool_true"]
        assert cpp_result["bool_false"] == obj["bool_false"]
        assert cpp_result["null_val"] == obj["null_val"]
        assert cpp_result["array"] == obj["array"]
        assert cpp_result["nested_obj"] == obj["nested_obj"]

        cpp_sisl = sislc.dumps(obj)
        py_result = pysisl.loads(cpp_sisl)
        assert py_result["string"] == obj["string"]
        assert py_result["integer"] == obj["integer"]
