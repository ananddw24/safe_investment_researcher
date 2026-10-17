.PHONY: serve build validate export check-ids

serve:
	pip install -r requirements.txt
	mkdocs serve

build:
	pip install -r requirements.txt
	mkdocs build --strict

validate:
	pip install -r scripts/requirements-dev.txt
	python scripts/validate_data.py
	python scripts/check_ids.py

export:
	pip install -r scripts/requirements-dev.txt
	python scripts/export_resources_json.py

check-ids:
	pip install -r scripts/requirements-dev.txt
	python scripts/check_ids.py
