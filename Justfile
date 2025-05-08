@default:
  @just --list

# Remove dist and egg-info
@clean:
  -rm dist/*
  -rmdir dist
  -rm index_images.egg-info/*
  -rmdir index_images.egg-info

# Run lint, check, test, and pyproject-build
@build: lint check test
  uv build

# Run pyproject-build (no lint, check, or test)
@build-only:
  uv build

# ruff format --check
@check:
  uv run ruff format --check

# ruff format
@format:
  uv run ruff format

# ruff check
@lint:
  uv run ruff check

# pytest
@test:
  uv run pytest
