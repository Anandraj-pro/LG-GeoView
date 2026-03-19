.PHONY: test lint format coverage

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=src --cov-report=term-missing

lint:
	flake8 src/ app.py

format:
	black src/ app.py tests/
