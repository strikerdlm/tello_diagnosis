# Contributing to Tello Diagnostics

Thank you for your interest in contributing to the Tello Diagnostics project! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

This project follows a standard Code of Conduct. By participating, you are expected to uphold this code. Please be respectful, inclusive, and considerate in all interactions.

## 🎯 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment details** (OS, Python version, Tello model)
- **Code samples or logs** (if applicable)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Rationale** - why is this enhancement needed?
- **Use cases** - how would this be used?
- **Alternatives considered**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for any new functionality
4. **Update documentation** as needed
5. **Run the test suite** and ensure all checks pass
6. **Submit a pull request**

## 🔧 Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- (Optional) Docker for containerized testing

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/tello-diagnostics.git
cd tello-diagnostics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## 📏 Coding Standards

This project follows strict Python coding standards:

### Type Safety

- **Full type hints required** on all functions
- **No `Any` types** unless absolutely necessary
- **Strict mypy checking** must pass

```python
def process_data(value: int, name: str) -> Dict[str, Any]:
    """Process data with explicit types."""
    ...
```

### Code Quality

All code must pass:

- ✅ **Ruff** - Linting with all checks enabled
- ✅ **Black** - Code formatting (line length 88)
- ✅ **isort** - Import sorting
- ✅ **mypy** - Type checking (strict mode)
- ✅ **Bandit** - Security scanning
- ✅ **pytest** - All tests passing

Run checks locally:

```bash
# Run all checks
ruff check src/ tests/
black --check src/ tests/
isort --check-only src/ tests/
mypy src/
bandit -r src/ -c pyproject.toml
pytest

# Auto-fix formatting issues
black src/ tests/
isort src/ tests/
ruff check --fix src/ tests/
```

### Code Style Rules

1. **No recursion** - Use iterative approaches
2. **Bounded loops** - All loops must have explicit termination
3. **Finite timeouts** - All I/O operations must have timeouts
4. **Context managers** - Use for all resources (files, sockets, etc.)
5. **Explicit error handling** - Never use bare `except:`
6. **Input validation** - Validate all inputs with clear error messages
7. **Immutable defaults** - Never use mutable default arguments
8. **No global state** - Pass state explicitly
9. **Pure functions preferred** - Minimize side effects
10. **Comprehensive docstrings** - Google-style format

### Documentation

- **All public functions** must have docstrings
- **Google-style format** for docstrings
- **Include type information** in docstrings
- **Document exceptions** that may be raised
- **Provide examples** for complex functions

Example:

```python
def validate_distance(distance: int, min_val: int = 20, max_val: int = 500) -> None:
    """
    Validate movement distance is within acceptable range.

    Args:
        distance: Distance value to validate in centimeters
        min_val: Minimum acceptable distance (default: 20)
        max_val: Maximum acceptable distance (default: 500)

    Raises:
        ValueError: If distance is outside acceptable range

    Example:
        >>> validate_distance(100)  # OK
        >>> validate_distance(10)   # Raises ValueError
    """
    if not (min_val <= distance <= max_val):
        raise ValueError(f"Distance must be between {min_val} and {max_val} cm")
```

## 🧪 Testing

### Writing Tests

- **Test coverage required** for all new code
- **Use pytest** framework
- **Mock external dependencies** (Tello drone)
- **Test error cases** as well as success cases
- **Use descriptive test names**

Example test:

```python
def test_connect_success(mock_tello_class: MagicMock) -> None:
    """Test successful connection to Tello."""
    mock_instance = MagicMock()
    mock_instance.get_current_state.return_value = {"bat": 85}
    mock_tello_class.return_value = mock_instance

    diagnostics = TelloDiagnostics()
    result = diagnostics.connect()

    assert result is True
    assert diagnostics.connected is True
    mock_instance.connect.assert_called_once()
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov --cov-report=html

# Run specific test
pytest tests/test_diagnostics.py::TestTelloDiagnostics::test_connect_success

# Run with verbose output
pytest -v
```

## 📝 Commit Messages

Use clear, descriptive commit messages:

- **Present tense** - "Add feature" not "Added feature"
- **Imperative mood** - "Move cursor to..." not "Moves cursor to..."
- **Reference issues** - Include issue number if applicable

Examples:

```
Add battery monitoring with low-power warnings

Fix timeout issue in connection retry logic (#42)

Refactor logger to use pathlib instead of os.path

Update documentation for Docker deployment
```

## 🚀 Pull Request Process

1. **Ensure all tests pass** and code quality checks succeed
2. **Update documentation** if adding features or changing behavior
3. **Add tests** for new functionality
4. **Update CHANGELOG.md** with your changes
5. **Link related issues** in the PR description
6. **Wait for review** - maintainers will review your PR

### PR Checklist

- [ ] Tests pass locally
- [ ] Code quality checks pass (ruff, black, mypy, bandit)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Tests added for new features
- [ ] No breaking changes (or documented if unavoidable)

## 🔒 Security

- **Never commit secrets** or API keys
- **Validate all inputs** to prevent injection attacks
- **Use safe defaults** for all operations
- **Report security issues privately** to dlmalpica@me.com

## 🏷️ Versioning

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backward compatible)
- **PATCH** version for bug fixes (backward compatible)

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 💬 Questions?

- **Open an issue** for general questions
- **Email maintainer** at dlmalpica@me.com for private inquiries
- **Check documentation** in the `Docs/` directory

## 🙏 Thank You!

Your contributions make this project better for everyone. Thank you for taking the time to contribute!

