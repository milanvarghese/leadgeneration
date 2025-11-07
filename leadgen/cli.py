from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable, List

from .filters import apply_budget_filter
from .models import Lead, deduplicate
from .sources import YellowPagesScraper


DEFAULT_QUERIES = [
    "digital marketing",
    "marketing consultant",
    "startup consultant",
    "venture capital",
    "coworking space",
    "business accelerator",
]


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lead generation scraper for Philadelphia-area growth businesses.",
    )
    parser.add_argument("--city", default="Philadelphia", help="City to target (default: Philadelphia)")
    parser.add_argument("--state", default="PA", help="State/region abbreviation (default: PA)")
    parser.add_argument(
        "--query",
        "-q",
        action="append",
        dest="queries",
        help="Search query to run on YellowPages. Can be repeated.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=2,
        help="Number of result pages to fetch per query.",
    )
    parser.add_argument(
        "--budget-min",
        type=int,
        default=3000,
        help="Minimum budget threshold for filtering (default: 3000).",
    )
    parser.add_argument(
        "--budget-max",
        type=int,
        default=5000,
        help="Maximum budget threshold for filtering (default: 5000).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("leads.csv"),
        help="Path to the CSV file where leads will be stored.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional path for writing a JSON export of the leads.",
    )
    parser.add_argument(
        "--include-raw",
        action="store_true",
        help="Include analytics and extra metadata in the JSON output.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def collect_leads(args: argparse.Namespace) -> List[Lead]:
    queries = args.queries or DEFAULT_QUERIES
    scraper = YellowPagesScraper(city=args.city, state=args.state)

    leads: List[Lead] = []
    for query in queries:
        scraped = scraper.fetch(query, max_pages=args.max_pages)
        leads.extend(scraped)

    leads = deduplicate(leads)
    leads = apply_budget_filter(leads, minimum=args.budget_min, maximum=args.budget_max)
    return sorted(leads, key=lambda lead: lead.growth_score or 0, reverse=True)


def write_csv(leads: Iterable[Lead], path: Path) -> None:
    fieldnames = [
        "name",
        "location",
        "description",
        "phone",
        "website",
        "categories",
        "source",
        "rating",
        "review_count",
        "estimated_budget_low",
        "estimated_budget_high",
        "growth_score",
    ]
    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for lead in leads:
            writer.writerow(lead.to_dict())


def write_json(leads: Iterable[Lead], path: Path, include_raw: bool) -> None:
    payload = [lead.to_dict(include_raw=include_raw) for lead in leads]
    with path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)
    leads = collect_leads(args)
    if not leads:
        print("No leads matched the requested filters.")
        return

    write_csv(leads, args.output)
    if args.json_output:
        write_json(leads, args.json_output, include_raw=args.include_raw)

    print(f"Saved {len(leads)} leads to {args.output}")
    if args.json_output:
        print(f"Saved JSON export to {args.json_output}")


if __name__ == "__main__":
    main()
