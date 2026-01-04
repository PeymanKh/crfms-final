install:
	pip install -e ".[dev]"

test:
	python3 -m pytest -v

lint:
	ruff check .

format:
	black .
