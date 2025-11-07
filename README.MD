# Lead Generation Toolkit

This repository provides a focused toolkit for sourcing high-value leads for web design and development engagements in the Greater Philadelphia area. The initial integration targets YellowPages listings to discover marketing-forward businesses and startups that are likely to invest \$3k–\$5k in a new website or growth engagement.

## Features

- **YellowPages scraper** tailored for Philadelphia businesses searching for marketing, growth, and startup services.
- **Budget heuristics** that flag companies with advertising activity, digital presence, and growth-oriented descriptions.
- **Command-line interface** that exports qualified leads to CSV (and optionally JSON) for quick outreach workflows.

## Quick start

Create a virtual environment and install the project:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Run the scraper with the default Philadelphia-focused queries:

```bash
leadgen --max-pages 2 --budget-min 3000 --budget-max 5000 --output leads.csv --json-output leads.json --include-raw
```

The command will:

1. Query YellowPages for a curated set of growth-oriented keywords (digital marketing, startup consultants, venture capital, coworking, and more).
2. Deduplicate the raw listings.
3. Score and filter leads to those whose estimated budget range intersects \$3k–\$5k.
4. Export the result set to CSV/JSON for follow-up.

To customize the search keywords, repeat the `--query` flag:

```bash
leadgen --query "legal services" --query "financial advisor" --budget-min 3500 --budget-max 6000
```

## Extending the toolkit

- Add new scrapers under `leadgen/sources/` following the same pattern as the YellowPages scraper.
- Enhance the heuristics in `leadgen/filters.py` to reflect additional qualification signals (e.g., employee counts, funding rounds, tech stack checks).
- Wire alternative storage targets (Airtable, Google Sheets, CRMs) by adapting the CLI output stage.

## Running tests

```bash
pytest
```
