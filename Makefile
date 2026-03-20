.PHONY: test lint format coverage snapshot

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=src --cov-report=term-missing

lint:
	flake8 src/ app.py

format:
	black src/ app.py tests/

snapshot:
	@mkdir -p data/snapshots
	@cp "data/West_Campus_Care_Groups_Area 2026.xlsx" "data/snapshots/snapshot_$$(date +%Y-%m-%d_%H%M%S).xlsx"
	@echo "Snapshot saved to data/snapshots/"
