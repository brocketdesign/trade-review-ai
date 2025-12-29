# Contributing to Trade Review AI

Thank you for your interest in contributing to Trade Review AI! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment for all contributors

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Python version, OS, etc.)

### Suggesting Features

For feature requests, please create an issue describing:
- The problem you're trying to solve
- Your proposed solution
- Why this would be valuable
- Any alternative approaches you've considered

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** following the guidelines below
4. **Test your changes**: Ensure all tests pass
5. **Commit your changes**: Use clear, descriptive commit messages
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Create a Pull Request**: Provide a clear description of your changes

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and small (single responsibility)
- Use descriptive variable names

### Architecture Principles

- **Modularity**: Keep components independent and focused
- **Determinism**: Ensure analysis methods produce consistent results
- **Extensibility**: Design for easy extension and modification
- **Documentation**: Code should be self-documenting with clear names

### Testing

- Write tests for new functionality
- Ensure existing tests still pass
- Use `test_system.py` as a reference for test structure
- Test edge cases and error conditions

### Documentation

- Update README.md if adding user-facing features
- Update TECHNICAL.md for architectural changes
- Include docstrings with:
  - Function/class purpose
  - Parameter descriptions
  - Return value descriptions
  - Example usage (where helpful)

### Commit Messages

Use clear, descriptive commit messages:

```
Good: "Add support for multiple timeframes in market analysis"
Good: "Fix incorrect R:R ratio calculation for sell trades"
Bad: "Update code"
Bad: "Fix bug"
```

## Areas for Contribution

### High Priority

1. **Additional Data Sources**
   - Direct TradingView API integration
   - Support for other data formats (JSON, databases)
   - Real-time data streaming

2. **Enhanced Analysis**
   - Additional technical indicators
   - Pattern recognition
   - Multi-timeframe analysis

3. **Improved Visualizations**
   - Chart generation
   - Trade visualization
   - Performance dashboards

### Documentation

- Tutorial videos or articles
- Additional examples
- Translation to other languages
- API documentation improvements

### Testing

- Expand test coverage
- Add integration tests
- Performance benchmarking
- Edge case testing

## Questions?

If you have questions about contributing, please:
1. Check existing issues and documentation
2. Create a new issue with the "question" label
3. Be specific about what you need help with

## License

By contributing to Trade Review AI, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be acknowledged in the project documentation. Thank you for helping improve Trade Review AI!
