# Introligo Test Suite

This directory contains comprehensive unit tests for the Introligo project.

## Test Coverage

- **Statement Coverage**: 100%
- **Branch Coverage**: 99%
- **Total Tests**: 126
- **Test Files**: 10

## Test Structure

### Test Files

1. **test_error.py** - Tests for `IntroligoError` exception class
2. **test_utils.py** - Tests for utility functions (`slugify`, `count_display_width`)
3. **test_include_loader.py** - Tests for YAML `IncludeLoader` with `!include` directive support
4. **test_page_node.py** - Tests for `PageNode` class and hierarchy management
5. **test_generator.py** - Comprehensive tests for `IntroligoGenerator` class
6. **test_main.py** - Tests for main CLI entry point
7. **test_main_block.py** - Tests for `__main__` execution
8. **test_coverage.py** - Additional edge case tests for 100% coverage
9. **conftest.py** - Pytest fixtures and configuration
10. **__init__.py** - Test package initialization

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with coverage report
```bash
pytest tests/ --cov=introligo --cov-report=term-missing --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_generator.py -v
```

### Run specific test class or function
```bash
pytest tests/test_generator.py::TestIntroligoGeneratorInit -v
pytest tests/test_utils.py::TestSlugify::test_slugify_basic -v
```

## Test Categories

### Unit Tests
- Error handling and custom exceptions
- Utility functions (text processing, display width calculation)
- YAML loading with includes
- Page node hierarchy management
- RST content generation
- Template processing
- Markdown conversion

### Integration Tests
- Full documentation generation workflow
- CLI argument parsing and execution
- File writing and directory structure creation
- Doxygen configuration generation

### Edge Case Tests
- Invalid YAML handling
- Missing file error handling
- Path resolution edge cases
- Strict vs. non-strict mode
- Dry-run mode
- Complex markdown conversion scenarios

## Fixtures

Common fixtures provided in `conftest.py`:
- `temp_dir` - Temporary directory for test files
- `sample_yaml_config` - Basic YAML configuration
- `sample_include_config` - Configuration with `!include` directives
- `doxygen_config` - Configuration with Doxygen settings
- `markdown_file` - Sample markdown file
- `config_with_markdown` - Configuration that includes markdown

## Coverage Configuration

Coverage settings are defined in `pyproject.toml`:
- Branch coverage enabled
- Exclusion of `if __name__ == "__main__":` guards
- HTML coverage reports generated in `htmlcov/` directory

## Test Best Practices

1. **Isolation**: Each test uses temporary directories and doesn't affect global state
2. **Fixtures**: Reusable test data through pytest fixtures
3. **Mocking**: Strategic use of mocks for testing error paths and edge cases
4. **Descriptive Names**: Clear test names describing what is being tested
5. **Organization**: Tests grouped by functionality in classes
6. **Coverage**: Comprehensive coverage of all code paths including error handling

## Continuous Integration

These tests are designed to run in CI/CD pipelines with:
- Python 3.8+
- pytest and pytest-cov
- All project dependencies installed
