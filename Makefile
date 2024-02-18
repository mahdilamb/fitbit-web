.PHONY: help tests ruff isort docstrings format mypy qc api requirements
default: help

MAIN_PACKAGE_DIRECTORY="fitbit_web"
PYTHON_SRC_DIRECTORIES=${MAIN_PACKAGE_DIRECTORY} "tests" "builder"

tests: # Run tests using pytest.
	pytest --cov=${MAIN_PACKAGE_DIRECTORY} --cov-report term-missing

ruff: # Format the python files using ruff.
	ruff check --fix ${PYTHON_SRC_DIRECTORIES}

isort: # Sort the imports in python files.
	isort ${PYTHON_SRC_DIRECTORIES}

bandit: # Run security checks with bandit.
	bandit -r ${MAIN_PACKAGE_DIRECTORY}

docstrings:  # Format the docstrings using docformatter
	docformatter --in-place -r ${PYTHON_SRC_DIRECTORIES};  pydocstyle ${PYTHON_SRC_DIRECTORIES}

format: isort ruff docstrings # Format the source files with isort and ruff.

mypy: # Check types with mypy.
	mypy ${MAIN_PACKAGE_DIRECTORY}

qc: format tests bandit mypy # Run all the QC tasks.
api: PYTHONPATH=$(shell pwd)
api: # Generate the Mixin for the FitbitWebAPI
	python3 -m builder

requirements: # Save the versions being used
	@pip-compile pyproject.toml -o requirements.txt

help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m\n\t$$(echo $$l | cut -f 2- -d'#')\n"; done
