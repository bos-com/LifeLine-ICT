# Contributing to LifeLine-ICT

Thank you for your interest in contributing to LifeLine-ICT! This project is an ICT-Driven Disaster Preparedness & Early Warning system developed by the Bugema Open Source Community (BOSC).

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

- Use the GitHub issue tracker to report bugs
- Include detailed steps to reproduce the issue
- Provide environment information (Python version, OS, etc.)
- Include error logs and screenshots if applicable

### Suggesting Enhancements

- Use the GitHub issue tracker with the "enhancement" label
- Describe the problem and proposed solution
- Consider the impact on existing functionality

### Code Contributions

We welcome contributions in the following areas:

- **Bug Fixes**: Fix issues in the backend API, IoT layer, or documentation
- **New Features**: Add new endpoints, sensors, or analytics capabilities
- **Documentation**: Improve and expand project documentation
- **Testing**: Add tests for existing functionality
- **IoT Development**: Improve sensor firmware and logging

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- pip or uv for dependency management
- Optional: uvicorn for local development

### Getting Started

1. **Fork the Repository**

   Click the "Fork" button on the repository page.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/YOUR-USERNAME/LifeLine-ICT.git
   cd LifeLine-ICT
   ```

3. **Create a Virtual Environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate   # Windows
   ```

4. **Install Dependencies**

   ```bash
   pip install -r backend/requirements.txt
   ```

5. **Run the Development Server**

   ```bash
   uvicorn backend.app.main:app --reload
   ```

The API will be available at `http://127.0.0.1:8000` with OpenAPI documentation at `/docs`.

## Coding Standards

### Python Best Practices

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write descriptive variable and function names
- Keep functions small and focused
- Add docstrings to all functions and classes

### Project Structure

Follow the layered architecture:

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── services/     # Business logic
│   ├── repositories/ # Data access
│   ├── models/      # Database models
│   └── schemas/      # Pydantic schemas
├── tests/            # Test files
└── requirements.txt # Dependencies
```

### Git Conventions

- Branch from `main`: `git checkout -b feature/your-feature`
- Use clear, descriptive commit messages
- Keep commits focused and atomic

## Testing

### Running Tests

```bash
pytest backend/tests
```

### Writing Tests

- Write tests for all new functionality
- Cover both success and failure cases
- Use descriptive test names
- The test suite uses an in-memory SQLite database

### Test Coverage

- Aim to maintain or improve test coverage
- Cover service-level rules (business logic)
- Cover API contracts (endpoint behavior)

## Submitting Changes

### Pull Request Checklist

Before submitting your pull request:

- [ ] Code follows the coding standards
- [ ] Tests pass: `pytest backend/tests`
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts exist

### After Submitting

- Respond to review comments promptly
- Make requested changes
- Keep the PR updated with latest changes

## Module Overview

- `iot/` – Firmware sketches and logging scripts for field sensors
- `backend/` – FastAPI application, domain models, services, and tests
- `docs/` – Supplemental guides and design notes

## Questions or Need Help?

- Check existing documentation in `docs/`
- Search existing issues and discussions
- Contact the maintainers

## Recognition

Contributors will be recognized in the project documentation and release notes.

## Thank You!

Your contributions help protect communities from climate risks like floods and droughts. Every line of code, bug report, or documentation improvement makes a difference.

---

**Together, we can build safer communities** 🌍🚨

*Made with ❤️ by the BOSC Team*