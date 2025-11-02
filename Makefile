.PHONY: install install-dev format lint check test run dry-run stats clean

install:
	poetry install

install-dev:
	poetry install --with dev

format:
	poetry run ruff format zcash_dca.py

lint:
	poetry run ruff check zcash_dca.py

check: format lint

run:
	poetry run zcash-dca run --amount_eur=$(AMOUNT)

dry-run:
	poetry run zcash-dca run --amount_eur=$(AMOUNT) --dry_run=True

stats:
	poetry run zcash-dca show_stats

clean:
	rm -rf __pycache__
	rm -rf .ruff_cache
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
