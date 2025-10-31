# Contributing to Smart Door Driver

Thank you for your interest in contributing to the Smart Door Driver project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

## How to Contribute

### Reporting Bugs

When reporting bugs, please include:
- A clear description of the issue
- Steps to reproduce the problem
- Expected vs actual behavior
- System information (OS, compiler version, etc.)
- Relevant code snippets or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:
- A clear description of the proposed feature
- Use cases and benefits
- Possible implementation approach
- Any potential drawbacks or concerns

### Pull Requests

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/smart-door-driver.git
   cd smart-door-driver
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Write clean, readable code
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation as needed

4. **Test Your Changes**
   - Ensure code compiles without warnings
   - Test all functionality
   - Add unit tests if applicable

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

6. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### C++ Guidelines

- **Naming Conventions**:
  - Classes: PascalCase (e.g., `SmartDoor`)
  - Methods: camelCase (e.g., `getState()`)
  - Private members: camelCase with no prefix (e.g., `currentState`)
  - Constants: UPPER_SNAKE_CASE (e.g., `MAX_ATTEMPTS`)

- **Documentation**:
  - Use Doxygen-style comments for all public APIs
  - Include `@brief`, `@param`, and `@return` tags
  - Document complex algorithms and state transitions

- **Code Style**:
  - Indent with 4 spaces (no tabs)
  - Opening braces on same line for methods
  - Use `nullptr` instead of `NULL`
  - Prefer references over pointers when possible

### Example

```cpp
/**
 * @brief Open the door
 *
 * This method unlocks the servo and extends the contractor
 * to physically open the door.
 *
 * @return true if door opened successfully, false otherwise
 */
bool SmartDoor::open() {
    if (!isSafeToOperate()) {
        return false;
    }

    // Implementation...
    return true;
}
```

## Documentation

When adding or modifying features:

1. Update relevant header file Doxygen comments
2. Update or add usage examples in the configuration
3. Update README.md if needed
4. Add entries to CHANGELOG.md

## Building Documentation

```bash
cd examples/complex_project
./build_docs.sh
```

## Questions?

If you have questions, feel free to:
- Open an issue for discussion
- Reach out to maintainers
- Check existing documentation

Thank you for contributing!
