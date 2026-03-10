# Pre-Commit Setup

This repository uses [pre-commit](https://pre-commit.com/) to run automated checks and formatting before commits.

## Installation

### 1. Install pre-commit

```bash
pip install pre-commit
```

### 2. Install the git hooks

```bash
pre-commit install
```

This will install the pre-commit hooks into your `.git/hooks` directory.

## Usage

### Automatic (Recommended)

Once installed, pre-commit hooks will run automatically before each `git commit`.

If any checks fail, your commit will be rejected, and the output will show what needs to be fixed.

### Manual

To run pre-commit checks manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on files changed since the main branch
pre-commit run --from-ref origin/18.0 --to-ref HEAD

# Run a specific hook
pre-commit run black --all-files
```

## Included Hooks

- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures files end with a newline
- **check-yaml**: Validates YAML files
- **check-added-large-files**: Prevents committing large files
- **debug-statements**: Checks for debugger imports and breakpoints
- **fix-byte-order-marker**: Removes byte order markers
- **black**: Python code formatter
- **isort**: Python import sorter
- **flake8**: Python linter
- **pyupgrade**: Upgrades Python syntax
- **prettier**: Formats JavaScript, YAML, JSON, Markdown, and XML
- **oca-license-header**: Validates AGPL-3 license headers
- **manifest-required-keys**: Checks `__manifest__.py` has required keys
- **manifest-version-format**: Validates `__manifest__.py` version format
- **odoo-module-noupdate**: Checks `<odoo>` tags in XML files

## Configuration Files

- `.pre-commit-config.yaml` - Main pre-commit configuration
- `.pre-commit-config.mirror.yaml` - Mirror configuration for OCA deployment
- `.editorconfig` - Editor configuration for consistent formatting
- `.flake8` - Flake8 linter configuration
- `pyproject.toml` - Black and isort configurations
- `.gitignore` - Git ignore patterns

## Updating Hooks

To update all pre-commit hooks to their latest versions:

```bash
pre-commit autoupdate
```

## Troubleshooting

### Pre-commit isn't running

Make sure hooks are installed:

```bash
pre-commit install
```

### I want to bypass pre-commit checks

You can skip pre-commit checks using:

```bash
git commit --no-verify
```

However, this is **not recommended** as it bypasses code quality checks.

### How do I fix common failures?

Most hooks will auto-fix issues. Just re-stage the files and commit again:

```bash
git add .
git commit
```

For manual fixes, run:

```bash
# Auto-format Python code
black .

# Sort imports
isort .

# Format XML/YAML/JSON/Markdown
prettier --write "**/*.{xml,yml,yaml,json,md}"
```

## Code Quality Standards

This configuration ensures code quality, consistency, and license compliance for Odoo 18.0 private modules. It is based on OCA best practices but adapted for private customer development.
