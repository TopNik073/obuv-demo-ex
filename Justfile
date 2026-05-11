# Directory for source code
SOURCE_DIR := "src"

# Default command: list available commands
default:
    @just --list

# Environment variables file
set dotenv-filename := ".env"

# Run all checks: linters and formatting validation
lint: ruff-check

# --- Dependency Management ---

# Update project dependencies
[group('dependencies')]
update:
    uv sync --upgrade

# Sync project dependencies
[group('dependencies')]
sync:
    uv sync

# --- Linters and Formatting ---

# Automatically format code
[group('linters')]
ruff-format:
    python -m ruff check --fix --unsafe-fixes {{ SOURCE_DIR }}
    python -m ruff format .

# Lint code using Ruff
[group('linters')]
ruff-check:
    python -m ruff check {{ SOURCE_DIR }}


# Lint with def-form
[group('linters')]
def-form-check:
    def-form check src
