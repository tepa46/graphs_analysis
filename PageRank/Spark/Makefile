VENV_DIR      ?= .venv
PYTHON        ?= python3
PIP           ?= $(PYTHON) -m pip
ENTRY_POINT   ?= main.py

.PHONY: venv

venv:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m venv $(VENV_DIR)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: 
	$(VENV_DIR)/bin/$(PYTHON) $(ENTRY_POINT)


