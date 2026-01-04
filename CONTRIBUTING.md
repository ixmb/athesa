# Contributing to Athesa

Thank you for your interest in contributing to Athesa! This document provides guidelines and instructions for contributing.

---

## 🎯 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and environment details

### Suggesting Features

Feature requests are welcome! Please:
- Check existing issues first
- Clearly describe the use case
- Explain why it would benefit users

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run tests**:
   ```bash
   pytest tests/
   ```
6. **Commit with clear messages**:
   ```bash
   git commit -m "Add: feature description"
   ```
7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request**

---

## 📋 Development Setup

### Clone the repository

```bash
git clone https://github.com/ixmb/athesa.git
cd athesa
```

### Install in development mode

```bash
pip install -e ".[dev]"
```

### Run tests

```bash
# All tests
pytest

# With coverage
pytest --cov=athesa tests/

# Specific test file
pytest tests/unit/test_events.py -v
```

---

## 🎨 Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use `black` for formatting:
  ```bash
  black athesa/
  ```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `ProcessRunner`)
- **Functions/Methods**: `snake_case` (e.g., `create_action_sequence`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `ACTION_COMMAND`)
- **Private**: prefix with `_` (e.g., `_check_criteria`)

### Documentation

- All public APIs must have docstrings
- Use Google-style docstrings
- Include examples in docstrings where helpful

Example:
```python
def create_action_sequence(self, context: ProcessContext) -> ActionSequence:
    """
    Generate action sequence for this screen.
    
    Args:
        context: Process execution context
        
    Returns:
        ActionSequence with actions and next state
        
    Example:
        >>> handler = MyHandler()
        >>> sequence = handler.create_action_sequence(context)
        >>> print(len(sequence.actions))
        3
    """
    pass
```

---

##  Testing Guidelines

### Unit Tests

- Test one thing per test
- Use descriptive test names: `test_<what>_<when>_<expected>`
- Keep tests independent
- Use fixtures for common setup

### Real-World Scenarios

- Tests should represent actual use cases
- Include error cases
- Test edge conditions

Example:
```python
def test_process_registry_multi_tenancy(self):
    """
    Scenario: SaaS platform with customer-specific processes
    
    Real use case: Each customer has different automation flows
    """
    registry = ProcessRegistry()
    # Test implementation...
```

---

## 🏗️ Project Structure

```
athesa/
├── athesa/           # Main package
│   ├── core/         # Protocols & interfaces
│   ├── engine/       # Execution components
│   ├── events/       # Event system
│   ├── adapters/     # Browser adapters
│   ├── factory/      # Process registry
│   └── exceptions/   # Framework exceptions
├── examples/         # Example implementations
├── tests/            # Test suite
│   ├── unit/         # Unit tests
│   └── integration/  # Integration tests
└── docs/             # Documentation
```

---

## 🔄 Git Workflow

### Commit Messages

Use conventional commits:
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `test:` test changes
- `refactor:` code refactoring
- `chore:` maintenance tasks

Examples:
```bash
feat: add Playwright adapter
fix: handle timeout in screen detection
docs: update API reference for ProcessRunner
test: add integration tests for login flow
```

### Branch Naming

- `feature/description` - new features
- `fix/description` - bug fixes
- `docs/description` - documentation
- `test/description` - test improvements

---

##  Release Process

1. Update version in `athesa/version.py`
2. Update `CHANGELOG.md`
3. Create release commit:
   ```bash
   git commit -m "chore: release v0.2.0"
   ```
4. Tag release:
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```
5. GitHub Actions will automatically publish to PyPI

---

## 📞 Questions?

- Open a [Discussion](https://github.com/ixmb/athesa/discussions)
- Ask in [Issues](https://github.com/ixmb/athesa/issues)

---

Thank you for contributing to Athesa! 
