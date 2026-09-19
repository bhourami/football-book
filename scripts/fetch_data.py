#!/usr/bin/env python3
"""Download and cache football-data.co.uk Premier League CSVs.

Free, no signup. Each season file carries full-time results, shots, shots on
target, and several bookmakers' opening and closing prices. The current
(2026-27) file additionally carries real expected goals (HxG/AxG); earlier
seasons do not.

Raw CSVs are cached under data/ and never committed -- see .gitignore.
"""
from __future__ import annotations

import csv
import json
import os
import urllib.request
from datetime import datetime, timezone

BASE = "https://www.football-data.co.uk/mmz4281/{season}/E0.csv"
SEASONS = ["2223", "2324", "2425", "2526", "2627"]
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def season_label(code: str) -> str:
    return f"20{code[:2]}-{code[2:]}"


def fetch(season: str, force: bool = False) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"E0_{season}.csv")
    if os.path.exists(path) and not force:
        return path
    url = BASE.format(season=season)
    with urllib.request.urlopen(url, timeout=60) as resp:
        body = resp.read()
    with open(path, "wb") as f:
        f.write(body)
    return path


def load(season: str) -> list[dict]:
    """Rows for one season, oldest first, with Date parsed and floats coerced."""
    path = fetch(season)
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    out = []
    for r in rows:
        if not r.get("HomeTeam") or not r.get("FTHG"):
            continue
        try:
            date = datetime.strptime(r["Date"], "%d/%m/%Y")
        except ValueError:
            continue
        rec = {
            "season": season,
            "date": date,
            "home": r["HomeTeam"].strip(),
            "away": r["AwayTeam"].strip(),
            "hg": int(r["FTHG"]),
            "ag": int(r["FTAG"]),
        }
        # Opening prices are what a bet would actually be struck at; closing
        # prices are the benchmark CLV is measured against.
        for key, col in (
            ("oh", "B365H"), ("od", "B365D"), ("oa", "B365A"),
            ("ch", "B365CH"), ("cd", "B365CD"), ("ca", "B365CA"),
        ):
            try:
                rec[key] = float(r[col])
            except (KeyError, TypeError, ValueError):
                rec[key] = None
        # Real xG, present only in the 2026-27 file at time of writing.
        for key, col in (("hxg", "HxG"), ("axg", "AxG")):
            try:
                rec[key] = float(r[col])
            except (KeyError, TypeError, ValueError):
                rec[key] = None
        out.append(rec)

    out.sort(key=lambda x: x["date"])
    return out


def load_all(seasons: list[str] | None = None) -> list[dict]:
    seasons = seasons or SEASONS
    matches: list[dict] = []
    for s in seasons:
        matches.extend(load(s))
    matches.sort(key=lambda x: x["date"])
    return matches


def write_manifest() -> None:
    manifest = {
        "source": "https://www.football-data.co.uk/data.php",
        "url_pattern": BASE,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "seasons": {},
    }
    for s in SEASONS:
        rows = load(s)
        manifest["seasons"][season_label(s)] = {
            "matches": len(rows),
            "with_closing_odds": sum(1 for r in rows if r["ch"]),
            "with_xg": sum(1 for r in rows if r["hxg"] is not None),
        }
    path = os.path.join(DATA_DIR, "manifest.json")
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    write_manifest()
