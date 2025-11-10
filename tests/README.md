# Test Suite

## Overview

Basic test suite for the Nominative Determinism Research Platform.

## Structure

```
tests/
├── __init__.py             # Test package initialization
├── conftest.py             # Pytest fixtures and configuration
├── test_base_analyzers.py  # Base analyzer class tests
├── test_blueprints.py      # Flask blueprint/route tests
└── README.md               # This file
```

## Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-cov
```

### Run All Tests

```bash
# From project root
python3 -m pytest tests/

# With coverage report
python3 -m pytest tests/ --cov=analyzers --cov=blueprints --cov-report=html

# Verbose output
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_base_analyzers.py

# Run specific test class
python3 -m pytest tests/test_base_analyzers.py::TestBaseLinguisticAnalyzer

# Run specific test method
python3 -m pytest tests/test_base_analyzers.py::TestBaseLinguisticAnalyzer::test_count_syllables_simple
```

### Run with Output

```bash
# See print statements
python3 -m pytest tests/ -s

# See detailed info
python3 -m pytest tests/ -vv
```

## Test Coverage

Current test coverage:

- **Base Analyzers**: ✅ Complete
  - BaseStatisticalAnalyzer: 80%
  - BaseLinguisticAnalyzer: 85%
  - BaseDomainAnalyzer: 75%
  - BaseBettingAnalyzer: 80%

- **Blueprints**: ✅ Basic
  - Core routes: Basic smoke tests
  - Betting routes: Basic smoke tests
  - Sports routes: Basic smoke tests
  - API endpoints: Basic connectivity tests

- **Collectors**: ❌ Not tested
- **Specific Analyzers**: ❌ Not tested
- **Data Models**: ❌ Not tested

## Test Strategy

### Unit Tests (Current)

Test individual components in isolation:
- Base analyzer methods
- Linguistic feature extraction
- Statistical calculations
- Betting calculations

### Integration Tests (Partial)

Test components working together:
- Flask routes responding
- API endpoints returning JSON
- Blueprint registration

### Missing Tests (Future)

- Database operations
- Data collector functionality
- Specific domain analyzers
- Template rendering
- Error handling
- Edge cases

## Adding New Tests

### 1. Create Test File

```bash
touch tests/test_new_feature.py
```

### 2. Write Tests

```python
import pytest

class TestNewFeature:
    def test_something(self):
        # Arrange
        input_data = "test"
        
        # Act
        result = function_to_test(input_data)
        
        # Assert
        assert result == expected_output
```

### 3. Run Tests

```bash
python3 -m pytest tests/test_new_feature.py
```

## Fixtures Available

From `conftest.py`:

- `app`: Flask application for testing
- `client`: Flask test client
- `sample_names`: Sample name data
- `sample_linguistic_features`: Sample feature dictionary

Use in tests:

```python
def test_with_client(client):
    response = client.get('/')
    assert response.status_code == 200
```

## Best Practices

1. **Test Independence**: Each test should run independently
2. **Clear Names**: Test names should describe what they test
3. **AAA Pattern**: Arrange, Act, Assert
4. **One Assert**: Prefer one logical assertion per test
5. **Fixtures**: Use fixtures for common setup

## Continuous Integration

To set up CI/CD:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov
```

## Test Database

Tests use in-memory SQLite database:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
```

No persistent data between tests.

## Mocking

For testing without external dependencies:

```python
from unittest.mock import Mock, patch

def test_with_mock():
    with patch('module.function') as mock_func:
        mock_func.return_value = "mocked"
        result = my_function()
        assert result == "mocked"
```

## Performance Testing

For performance-critical code:

```python
import time

def test_performance():
    start = time.time()
    result = slow_function()
    duration = time.time() - start
    assert duration < 1.0  # Should complete in under 1 second
```

## Known Issues

1. **Database Tests**: Need proper database fixtures
2. **API Tests**: Need better mock data
3. **Coverage**: Only ~20% of codebase currently tested

## Roadmap

- [ ] Add database model tests
- [ ] Add collector tests with mocked APIs
- [ ] Add domain analyzer tests
- [ ] Increase coverage to 80%+
- [ ] Add integration tests
- [ ] Add end-to-end tests
- [ ] Set up CI/CD
- [ ] Add performance tests

---

**Status**: Basic test suite operational  
**Coverage**: ~20% of codebase  
**Last Updated**: November 2025

