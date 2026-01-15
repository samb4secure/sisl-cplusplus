#!/usr/bin/env python3
"""
Run all SISL interoperability tests.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -v           # Verbose output
    python run_tests.py -k "split"   # Run only tests matching "split"
    python run_tests.py --tb=short   # Short traceback on failures
"""

import sys
import subprocess


def main():
    # Build pytest arguments
    args = [
        "python3", "-m", "pytest",
        "-v",  # Verbose by default
        "--tb=short",  # Short tracebacks
    ]

    # Add any command-line arguments passed to this script
    args.extend(sys.argv[1:])

    # Run from the tests directory
    result = subprocess.run(args)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
