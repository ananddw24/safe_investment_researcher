.PHONY: serve build validate export check-ids kb catalog lint test

serve:
	pip install -r requirements.txt
	mkdocs serve

catalog:
	pip install -r scripts/requirements-dev.txt
	python3 scripts/generate_resources_catalog.py

build: catalog
	pip install -r requirements.txt
	mkdocs build --strict

validate:
	pip install -r scripts/requirements-dev.txt
	python3 scripts/validate_data.py
	python3 scripts/check_ids.py

export:
	pip install -r scripts/requirements-dev.txt
	python3 scripts/export_resources_json.py

check-ids:
	pip install -r scripts/requirements-dev.txt
	python3 scripts/check_ids.py

kb:
	pip install -r scripts/requirements-dev.txt
	python3 scripts/build_kb_index.py
	python3 scripts/staleness_report.py

lint:
	pip install -r scripts/requirements-dev.txt
	ruff check scripts tests

test:
	pip install -r scripts/requirements-dev.txt
	python3 -m pytest

teaching:
	pip install -r scripts/requirements-dev.txt -r scripts/requirements-teaching.txt
	python3 scripts/generate_teaching_portfolio.py
