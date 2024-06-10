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
  pipenv run pyproject-build

# Run pyproject-build (no lint, check, or test)
@build-only:
  pipenv run pyproject-build

# ruff format --check
@check:
  pipenv run ruff format --check

# ruff format
@format:
  pipenv run ruff format

# ruff check
@lint:
  pipenv run ruff check

# pytest
@test:
  pipenv run pytest
