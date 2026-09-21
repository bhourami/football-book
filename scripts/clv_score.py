#!/usr/bin/env python3
"""Era 02 scoreboard — closing line value, per methodology.md section 15.

CLV is not a proxy for edge. Measured against the MARGIN-REMOVED closing
price, it is the edge, expressed as expected value:

    EV = fair_closing_probability * decision_price - 1

A selection with positive CLV makes money in the long run whether or not
it wins. One with negative CLV loses in the long run however often it
wins. That is why `result` is recorded in the ledgers and never scored.

Closing prices are DERIVED here, from data/E0_<season>.csv. Nothing in
this file will accept a hand-typed closing price -- three numbers in
Era 01 were typed rather than derived and all three were wrong in the
flattering direction.
"""
import argparse
import csv
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS = ("conclusion", "claude", "codex")

# football-data.co.uk closing columns, average across books.
COLS = {"home_win": "AvgCH", "draw": "AvgCD", "away_win": "AvgCA"}
TRIPLE = ("AvgCH", "AvgCD", "AvgCA")

# football-data.co.uk club names -> our three-letter codes
CODES = {
    "Arsenal": "ARS", "Aston Villa": "AVL", "Bournemouth": "BOU",
    "Brentford": "BRE", "Brighton": "BHA", "Chelsea": "CHE",
    "Coventry": "COV", "Crystal Palace": "CRY", "Everton": "EVE",
    "Fulham": "FUL", "Hull": "HUL", "Ipswich": "IPS", "Leeds": "LEE",
    "Liverpool": "LIV", "Man City": "MCI", "Man United": "MUN",
    "Newcastle": "NEW", "Nott'm Forest": "NFO", "Sunderland": "SUN",
    "Tottenham": "TOT",
}


def closing_table(season="2627"):
    """{'HOME-AWAY': {selection: (raw_close, fair_close, overround)}}"""
    path = os.path.join(ROOT, "data", f"E0_{season}.csv")
    if not os.path.exists(path):
        sys.exit(f"missing {path} -- run scripts/fetch_data.py first")
    out = {}
    for r in csv.DictReader(open(path)):
        try:
            key = f"{CODES[r['HomeTeam']]}-{CODES[r['AwayTeam']]}"
            prices = {s: float(r[c]) for s, c in COLS.items()}
        except (KeyError, ValueError):
            continue
        booksum = sum(1 / p for p in prices.values())
        out[key] = {s: (p, 1 / ((1 / p) / booksum), booksum - 1)
                    for s, p in prices.items()}
    return out


def score(entry, table):
    """Fill closing_price, clv_pp and ev_per_10_gbp. Returns True if scored."""
    fid = entry.get("fixture_id", "")
    key = fid[11:] if len(fid) > 11 else ""
    market = table.get(key)
    if market is None or entry["selection"] not in market:
        return False              # not yet in the data, or a BTTS selection
    raw, fair, ov = market[entry["selection"]]
    dp = entry["decision_price"]
    entry["closing_price"] = round(raw, 4)
    entry["closing_price_source"] = "football-data.co.uk E0 2026-27, AvgC (average close)"
    entry["closing_overround"] = round(ov, 5)
    entry["closing_fair_price"] = round(fair, 4)
    entry["clv_pp"] = round(((1 / fair) - (1 / dp)) * 100, 3)
    entry["ev_per_10_gbp"] = round(((1 / fair) * dp - 1) * 10, 3)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true",
                    help="write scores back into the ledgers")
    args = ap.parse_args()

    table = closing_table()
    all_clv, total = [], 0
    for book in BOOKS:
        path = os.path.join(ROOT, "ledger", f"{book}.json")
        d = json.load(open(path))
        scored = 0
        for e in d["entries"]:
            total += 1
            if e.get("clv_pp") is None:
                scored += bool(score(e, table))
            if isinstance(e.get("clv_pp"), (int, float)):
                all_clv.append(e["clv_pp"])
        d["selections_recorded"] = len(d["entries"])
        mine = [e["clv_pp"] for e in d["entries"] if isinstance(e.get("clv_pp"), (int, float))]
        d["median_clv_pp"] = round(statistics.median(mine), 3) if mine else None
        if args.write:
            json.dump(d, open(path, "w"), indent=2)
            open(path, "a").write("\n")
        print(f"{book:11} {len(d['entries']):3} selection(s), "
              f"{len(mine):3} scored, median CLV "
              f"{d['median_clv_pp'] if d['median_clv_pp'] is not None else '--'}")

    print(f"\n{total} selection(s) recorded, {len(all_clv)} scored, "
          f"decision point at 60")
    if all_clv:
        med = statistics.median(all_clv)
        print(f"MEDIAN CLV ACROSS ALL BOOKS: {med:+.3f}pp")
        if len(all_clv) >= 60:
            print("DECISION POINT REACHED:",
                  "continue" if med > 0 else
                  "median CLV is at or below zero -- section 15 says stop")
    else:
        print("MEDIAN CLV ACROSS ALL BOOKS: no scored selections yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
