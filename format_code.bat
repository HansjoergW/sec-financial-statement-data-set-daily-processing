@echo off
echo Running Black formatter...
black src

echo Running Ruff linter with fixes...
ruff check src --fix

echo Running Pylint...
pylint src

echo Formatting complete!
