# Python Linting & Formatting Quick Guide

## Tools Installed

- **Black** - Code formatter (opinionated, no config needed)
- **Flake8** - Linter (PEP8 compliance)
- **isort** - Import sorter

## Usage

### Format Code
```bash
# Format single file
black app.py

# Format all Python files
black .

# Check without changing
black --check .
```

### Lint Code
```bash
# Lint single file
flake8 app.py

# Lint all Python files
flake8 .
```

### Sort Imports
```bash
# Sort imports in file
isort app.py

# Sort all files
isort .
```

### Run All Checks
```bash
# Complete check
black --check . && flake8 . && isort --check .
```

## VS Code Integration

Auto-format on save is enabled in `.vscode/settings.json`.

**Format shortcut:** `Shift + Alt + F`

## Configuration Files

- `setup.cfg` - Flake8 and isort config
- `.vscode/settings.json` - VS Code integration

## Makefile Commands

```bash
# Format all code
make format

# Lint all code
make lint

# Both
make check
```
