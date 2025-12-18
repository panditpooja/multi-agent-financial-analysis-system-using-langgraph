#!/usr/bin/env python
"""
Test runner script for Multi-Agent Financial Analysis System.
"""
import sys
import subprocess

def run_tests():
    """Run all tests with pytest."""
    try:
        # Run pytest with coverage (note: actual code is in notebook, so coverage is limited to test code)
        result = subprocess.run(
            ["pytest", "tests/", "-v", "--tb=short"],
            check=False
        )
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install test dependencies:")
        print("  pip install -r requirements-test.txt")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)

