openapi:
	learnle generate-openapi

format:
	ruff format

test:
	pytest tests
	ruff check
	mypy
	ruff format --check
	learnle check-openapi
