#!/usr/bin/env python3
"""Turn a raw oddschecker capture into an Experiment 01 observation file.

The raw file records fractional odds exactly as they were displayed, one
entry per grid column including `null` for columns that were blank. This
script does the mechanical part only: parse fractions to decimals, drop
blanks, and split sportsbooks from exchanges. It makes no judgement about
prices and applies no part of the screen.

Kept separate from price_screen.py deliberately: transcription errors and
method errors should not be able to hide in the same file.

UNRESOLVED SPEC POINT -- exchanges. Pre-registration section 4 says to
capture "every bookmaker's price". Betfair Exchange and Matchbook are
exchanges, not bookmakers, and oddschecker itself lists them under a
separate "Exchanges" heading. They are written to `exchange_prices`, NOT
to `prices`, so the screen as run uses sportsbooks only. The values are
preserved so the other reading can be computed later without recapturing.
This is flagged for the owner in round-01.md rather than decided here.

No external dependencies.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def fractional_to_decimal(frac: str) -> float:
    """'11/10' -> 2.10. Fractional odds are profit-to-stake, so add 1."""
    num, den = frac.split("/")
    return round(int(num) / int(den) + 1.0, 6)


def build(raw: dict) -> dict:
    columns = raw["column_order"]
    exchanges = set(raw.get("exchanges", []))
    outcomes = raw["outcomes"]
    rows = raw["rows_fractional"]

    for outcome in outcomes:
        if len(rows[outcome]) != len(columns):
            raise ValueError(
                f"{outcome}: {len(rows[outcome])} values for {len(columns)} "
                "columns -- transcription is misaligned, refusing to build"
            )

    prices: dict[str, list[float]] = {}
    exchange_prices: dict[str, list[float]] = {}
    not_read: list[str] = []

    for i, book in enumerate(columns):
        raw_vals = [rows[o][i] for o in outcomes]
        if any(v is None for v in raw_vals):
            not_read.append(book)
            continue
        decimals = [fractional_to_decimal(v) for v in raw_vals]
        target = exchange_prices if book in exchanges else prices
        target[book] = decimals

    # The subject book must be present or there is nothing to measure.
    if "Ladbrokes" not in prices:
        raise ValueError("no Ladbrokes price in this capture")

    lad_index = raw["ladbrokes_column_index_1based"] - 1
    if columns[lad_index] != "Ladbrokes":
        raise ValueError("ladbrokes_column_index_1based disagrees with column_order")

    return {
        "fixture_id": raw["fixture_id"],
        "fixture": raw["fixture"],
        "market": raw["market"],
        "captured_at_utc": raw["captured_at_utc"],
        "source": raw["source"],
        "source_url": raw["source_url"],
        "outcomes": outcomes,
        "outcome_labels": raw.get("outcome_labels", {}),
        "prices": prices,
        "exchange_prices": exchange_prices,
        "exchanges_excluded_from_consensus": sorted(exchange_prices),
        "bookmakers_not_read": not_read,
        "prices_as_displayed": rows,
        "column_order": columns,
        "provenance": raw.get("ladbrokes_column_verified"),
        "notes": raw.get("notes", []),
    }


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("raw_files", nargs="+")
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for path in args.raw_files:
        raw = json.loads(Path(path).read_text())
        obs = build(raw)
        dest = out_dir / f"{obs['fixture_id']}-{obs['market']}.json"
        dest.write_text(json.dumps(obs, indent=2) + "\n")
        print(f"{dest}  {len(obs['prices'])} books, "
              f"{len(obs['exchange_prices'])} exchanges, "
              f"{len(obs['bookmakers_not_read'])} not read")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
