# Contributing to AI On UI

Thank you for your interest in contributing to AI On UI! All contributions are welcome and appreciated.

## Contributing Process

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

## Development Environment Setup

```bash
# Clone repository
git clone https://github.com/yourusername/aionui.git
cd aionui

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

## Coding Style

- Follow PEP 8
- Use Black for code formatting
- Google style docstrings
- Type hints for all functions/methods
- 100% test coverage for new code

## Testing

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=aionui

# Run tests for specific module
poetry run pytest tests/test_models
```

## Pull Request Guidelines

1. PRs must include a clear description of changes
2. Update documentation if needed
3. Add tests for new code
4. Ensure all tests pass
5. Code must be formatted with Black
6. No MyPy errors
7. Keep commit history clean and meaningful

## Feature Requests

I welcome new ideas! Create an issue with the [Feature Request] tag to propose new features.

## Bug Reports

When reporting bugs, please provide:

- Detailed description of the bug
- Steps to reproduce
- Complete logs
- Environment info (OS, Python version, etc.)
- Example code if possible

## License

By contributing, you agree that your contributions will be licensed under the MIT License.