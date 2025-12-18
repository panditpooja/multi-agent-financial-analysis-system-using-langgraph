# Test Suite for Multi-Agent Financial Analysis System

This directory contains unit tests for the Multi-Agent Financial Analysis System using LangGraph.

## Test Structure

- `test_alpha_vantage_tool.py` - Tests for Alpha Vantage tool date formatting
- `test_supervisor_loop_detection.py` - Tests for supervisor loop detection logic
- `test_agent_node.py` - Tests for agent node functionality
- `test_utils.py` - Tests for utility functions
- `test_integration.py` - Integration tests
- `conftest.py` - Pytest fixtures and configuration

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_alpha_vantage_tool.py
```

### Run with Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

## Test Coverage

The test suite covers:

1. **Date Formatting**: Tests for converting various date formats (ISO, compact, slash) to human-readable format
2. **Loop Detection**: Tests for detecting infinite loops when agents return identical responses
3. **Agent Node**: Tests for agent node execution, error handling, and Unicode cleaning
4. **Utility Functions**: Tests for event processing and helper functions
5. **Integration**: End-to-end tests for complete workflows

## Writing New Tests

When adding new tests:

1. Follow the naming convention: `test_*.py`
2. Use descriptive test function names starting with `test_`
3. Use fixtures from `conftest.py` when possible
4. Mock external dependencies (APIs, LLMs)
5. Test both success and error cases

## Example Test

```python
def test_example():
    """Test description."""
    # Arrange
    input_data = "test"
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_output
```

