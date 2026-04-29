# Troubleshooting Guide

## Common Issues

### 1. Virtual Environment Errors
If you get a "Command not found" error when running `python` or `pip`, ensure your virtual environment is activated:
- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

### 2. Dependency Installation Fails
Ensure you have the correct Python version installed and that your `pip` is up to date:
`python -m pip install --upgrade pip`
