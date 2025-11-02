ZCASH DCA BOT - SETUP COMMANDS
===============================

GITHUB REPOSITORY SETUP
-----------------------

Option 1 - Automated (recommended):
  ./setup_github.sh

Option 2 - Manual:
  git init
  git add .
  git commit -m "Initial commit: ZCash DCA bot with Decimal precision and Poetry"
  gh repo create zcash-dca-bot --private --description "Automated daily ZCash purchases on Kraken" --source=. --remote=origin
  git push -u origin main

Option 3 - Manual (public repo):
  git init
  git add .
  git commit -m "Initial commit: ZCash DCA bot with Decimal precision and Poetry"
  gh repo create zcash-dca-bot --public --description "Automated daily ZCash purchases on Kraken" --source=. --remote=origin
  git push -u origin main


PROJECT SETUP
-------------

1. Install Poetry:
   curl -sSL https://install.python-poetry.org | python3 -

2. Install dependencies:
   poetry install --with dev

3. Configure Kraken API:
   cp .env.example .env
   # Edit .env and add your KRAKEN_API_KEY and KRAKEN_SECRET_KEY

4. Test with dry run:
   poetry run zcash-dca run --amount_eur=50 --dry_run

5. Run real purchase:
   poetry run zcash-dca run --amount_eur=50


MAKE COMMANDS
-------------

make install-dev          # Install with dev dependencies
make format               # Format code with ruff
make lint                 # Lint code with ruff
make check                # Format and lint
make run AMOUNT=50        # Run purchase (requires AMOUNT variable)
make dry-run AMOUNT=50    # Test purchase (requires AMOUNT variable)
make stats                # Show statistics
make clean                # Clean cache files


DIRECT POETRY COMMANDS
----------------------

poetry run zcash-dca run --amount_eur=50              # Run purchase
poetry run zcash-dca run --amount_eur=50 --dry_run    # Test purchase
poetry run zcash-dca run --amount_eur=50 --post=False # Run without social post
poetry run zcash-dca show_stats                       # Show statistics


AUTOMATION SETUP
----------------

Cron (runs daily at 10:00 AM):
  crontab -e
  # Add this line:
  0 10 * * * cd /path/to/zcash-dca-bot && /usr/local/bin/poetry run zcash-dca run --amount_eur=50

Systemd Timer (Linux):
  See README.md for full systemd timer setup


DEVELOPMENT WORKFLOW
--------------------

1. Format code:
   poetry run ruff format zcash_dca.py

2. Lint code:
   poetry run ruff check zcash_dca.py

3. Auto-fix linting issues:
   poetry run ruff check --fix zcash_dca.py


DEPENDENCIES
------------

Runtime (3 trusted packages):
  - ccxt: Cryptocurrency exchange library
  - python-dotenv: Environment variable management
  - fire: CLI framework

Development (1 package):
  - ruff: Fast Python linter and formatter

All dependencies managed via Poetry (pyproject.toml)


FILES INCLUDED
--------------

zcash_dca.py        - Main Python script (363 lines, uses Decimal, dataclasses)
pyproject.toml      - Poetry configuration with ruff settings
Makefile            - Common tasks shortcuts
setup_github.sh     - Automated GitHub repository setup script
README.md           - Comprehensive documentation
.env.example        - Environment variable template
.gitignore          - Git ignore rules (excludes .env, cache, data)
SETUP_COMMANDS.txt  - This file


PYTHON VERSION
--------------

Requires Python 3.12+
Uses modern type hints (e.g., str | None instead of Optional[str])
