# Contributing to MOISSCode

Thank you for your interest in contributing to MOISSCode. This document provides guidelines for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/MOISSCode.git
   cd MOISSCode
   ```
3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```
4. Run the test suite to verify your setup:
   ```bash
   pytest tests/ -v
   ```

## Development Workflow

1. Create a branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run the test suite: `pytest tests/ -v`
4. Commit with a descriptive message
5. Push and open a Pull Request

## What We Accept

- Bug fixes with test coverage
- New clinical scoring systems, drug profiles, or lab tests
- Documentation improvements
- Performance optimizations
- Test coverage improvements

## Code Style

- Python 3.10+ syntax
- Type hints on all public method signatures
- Docstrings on all public functions (Google style)
- No trailing whitespace, consistent 4-space indentation

## Testing

- Every new feature must include tests
- Bug fixes should include a regression test
- Run the full suite before submitting: `pytest tests/ -v`

## Reporting Issues

Use [GitHub Issues](https://github.com/aethryva/MOISSCode/issues) to report bugs or request features. Please include:

- MOISSCode version (`moiss version`)
- Python version
- Operating system
- Minimal reproduction steps
- Expected vs actual behavior

## License

By contributing, you agree that your contributions will be licensed under the BSL 1.1 license.

## Questions?

Reach out at [dev@aethryva.com](mailto:dev@aethryva.com).
