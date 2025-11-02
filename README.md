# ZCash DCA Bot

Automated daily ZCash purchases on Kraken with Decimal precision and Poetry dependency management.

## Features

- **Decimal Precision**: All financial calculations use Python's Decimal class
- **Type Safety**: Dataclasses for Price, Quantity, Purchase, and AccumulationData  
- **Minimal Dependencies**: Only 3 trusted runtime dependencies
- **Modern Tooling**: Poetry for dependency management, Ruff for linting
- **Standard Library First**: Maximizes use of Python stdlib

## Requirements

- Python 3.12+
- Poetry for dependency management
- Kraken account with API access

## Quick Start

### 1. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Install Dependencies

```bash
poetry install --with dev
```

### 3. Configure Credentials

```bash
cp .env.example .env
# Edit .env and add your Kraken API credentials
```

### 4. Test

```bash
poetry run zcash-dca run --amount_eur=50 --dry_run
```

### 5. Run

```bash
poetry run zcash-dca run --amount_eur=50
```

## GitHub Setup Command

```bash
./setup_github.sh
```

Or manually:

```bash
git init
git add .
git commit -m "Initial commit: ZCash DCA bot with Decimal precision and Poetry"
gh repo create zcash-dca-bot --private --description "Automated daily ZCash purchases on Kraken" --source=. --remote=origin
git push -u origin main
```

## Usage

### Using Make

```bash
make install-dev          # Install with dev dependencies
make format               # Format code with ruff
make lint                 # Lint code with ruff  
make run AMOUNT=50        # Run purchase
make dry-run AMOUNT=50    # Test purchase
make stats                # Show statistics
```

### Using Poetry Directly

```bash
poetry run zcash-dca run --amount_eur=50
poetry run zcash-dca run --amount_eur=50 --dry_run
poetry run zcash-dca show_stats
```

## Architecture

### Classes

- **Price**: EUR amounts with Decimal precision
- **Quantity**: ZEC amounts with Decimal precision
- **Purchase**: Single transaction record
- **AccumulationData**: Aggregated purchase history
- **ZCashDCABot**: Main orchestrator

### Data Persistence

Stores purchase history in `zcash_accumulation.json`:

```json
{
  "total_zec": "1.23456789",
  "total_eur_spent": "500.00",
  "purchases": [...]
}
```

All numeric values stored as strings to preserve Decimal precision.

## Dependencies

Runtime (trusted, widely-used):
- **ccxt** ^4.4.0: Cryptocurrency exchange library
- **python-dotenv** ^1.0.1: Environment variable management
- **fire** ^0.7.0: CLI framework from Google

Development:
- **ruff** ^0.8.0: Fast Python linter and formatter

## Development

### Format Code

```bash
poetry run ruff format zcash_dca.py
```

### Lint Code

```bash
poetry run ruff check zcash_dca.py
```

### Auto-fix Issues

```bash
poetry run ruff check --fix zcash_dca.py
```

## Automation

### Cron (Linux/macOS)

```bash
crontab -e
```

Add:
```
0 10 * * * cd /path/to/zcash-dca-bot && /path/to/poetry run zcash-dca run --amount_eur=50
```

### Systemd Timer (Linux)

Create `/etc/systemd/system/zcash-dca.service`:

```ini
[Unit]
Description=ZCash DCA Daily Purchase

[Service]
Type=oneshot
User=yourusername
WorkingDirectory=/path/to/zcash-dca-bot
ExecStart=/usr/local/bin/poetry run zcash-dca run --amount_eur=50
```

Create `/etc/systemd/system/zcash-dca.timer`:

```ini
[Unit]
Description=Daily ZCash DCA Timer

[Timer]
OnCalendar=daily
OnCalendar=10:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl enable zcash-dca.timer
sudo systemctl start zcash-dca.timer
```

## Security

- Never commit `.env` file to version control
- Use API keys with minimal required permissions
- Test with small amounts first
- Store API keys securely

## Troubleshooting

**Invalid API key**: Verify credentials in `.env`

**Insufficient funds**: Ensure enough EUR in Kraken account

**Rate limiting**: Avoid running multiple instances simultaneously

**Poetry issues**: Update with `poetry self update`

## Disclaimer

This software is for educational purposes. Cryptocurrency trading involves significant risk. Only invest what you can afford to lose. The authors are not responsible for any financial losses.

## License

MIT License
