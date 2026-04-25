VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
MAIN = a_maze_ing.py

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) $(MAIN) config.txt

debug:
	$(PYTHON) -m pdb $(MAIN) config.txt

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache .venv *.pyc

lint:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(VENV)/bin/mypy . --strict