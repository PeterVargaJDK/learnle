openapi:
	learnle generate-openapi

prepare:
	learnle generate-openapi
	ruff format

format:
	ruff format

test:
	pytest tests
	ruff check
	mypy
	ruff format --check
	learnle check-openapi
