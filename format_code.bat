@echo off
echo Running Black formatter...
black src tests

echo Running Ruff linter with fixes...
ruff check src tests --fix

echo Running Pylint...
poetry run pylint src
poetry run pylint tests

echo Formatting complete!

