#!/usr/bin/env python3
"""Experiment 02 collector — spec/experiment-02-price-comparison.md.

Fetches Premier League match-result and BTTS prices from the-odds-api.com
and writes them as observations in the schema scripts/price_screen.py
already reads.

Why an API and not a scraped grid: Experiment 01 was halted because
oddschecker drops blank cells from the DOM, so one blank column silently
shifts every price by a position. Here each price arrives as a labelled
JSON field attached to a named bookmaker, so column alignment cannot fail
silently -- there are no columns.

Three rules this file enforces, all from the pre-registration:

  * Exchanges are NEVER blended into the sportsbook consensus (section 4,
    Benchmark B). Their margin sits in commission on net winnings rather
    than in the quoted price, so proportional margin removal does not mean
    the same thing for them. They are recorded separately.
  * The raw API response is written to disk unmodified before anything is
    derived from it (section 3). Nothing is discarded, including captures
    in which nothing qualifies.
  * Every capture is labelled with its scheduled slot, because the CLV
    series in section 8 depends on knowing when each price was seen.

Credit budget: cost is (markets x regions) = 2 credits per call. Five
captures per matchweek is ~10, eight matchweeks ~80, against a free tier
of 500/month. The experiment must not be redesigned to consume more.

Usage:
    python3 scripts/collect_odds.py --slot T-24h
    python3 scripts/collect_odds.py --from-raw <file>   # no credits spent

Needs ODDS_API_KEY in the environment or in .env (gitignored).
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPERIMENT = ROOT / "experiments" / "02-price-comparison"

API_HOST = "https://api.the-odds-api.com"
SPORT = "soccer_epl"
REGIONS = "uk"
# BTTS is NOT available on the bulk /odds endpoint (HTTP 422
# INVALID_MARKET). It is fetched per event; see fetch().
BULK_MARKETS = "h2h"

# Exchanges, not sportsbooks. Benchmark B -- recorded, never blended into
# the consensus the subject is measured against.
EXCHANGES = {"betfair_ex_uk", "matchbook", "smarkets"}

SUBJECT_KEY = "ladbrokes_uk"
SUBJECT_TITLE = "Ladbrokes"   # the name scripts/price_screen.py expects

# Books owned by the same operator as the subject. Ladbrokes and Coral are
# both Entain, and they quote near-identically -- Fulham v Man Utd on
# 20 Sept 2026 had both at exactly 1.50/2.45 on BTTS. Leaving Coral in the
# consensus would measure Ladbrokes partly against itself, which is the
# same error section 4 excludes Ladbrokes to avoid. Recorded, never blended.
SUBJECT_AFFILIATES = {"coral"}

# Books that are the same product under two brands. They quote identically,
# so counting both would let one pricing desk pull the median twice -- the
# concentration section 10(4) says must not drive a result. Each group
# contributes exactly one quote to the consensus; all members are preserved.
BOOK_GROUPS = {
    "livescorebet": "LiveScore Group",
    "virginbet": "LiveScore Group",
}

SLOTS = ("T-24h", "T-3h", "T-1h", "T-15m", "closing")


def load_api_key() -> str:
    env = ROOT / ".env"
    key = os.environ.get("ODDS_API_KEY")
    if not key and env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line.startswith("ODDS_API_KEY="):
                key = line.split("=", 1)[1].strip().strip("'\"")
                break
    if not key:
        sys.exit(
            "No ODDS_API_KEY found.\n"
            "  Sign up free at https://the-odds-api.com -- Starter tier, 500\n"
            "  credits/month, and this experiment needs about 80 for its whole\n"
            "  eight-week run.\n"
            f"  Then either export ODDS_API_KEY=... or add one line to {env}:\n"
            "      ODDS_API_KEY=your-key-here\n"
            "  (.env is gitignored; the key is never committed.)"
        )
    return key


def _get(api_key: str, path: str, **params) -> tuple[object, dict]:
    params.update({"apiKey": api_key})
    url = f"{API_HOST}{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r), {
                "requests_remaining": r.headers.get("x-requests-remaining"),
                "requests_used": r.headers.get("x-requests-used"),
                "last_request_cost": r.headers.get("x-requests-last"),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")[:400]
        sys.exit(f"the-odds-api returned HTTP {exc.code} for {path}: {body}")


def fetch(api_key: str, horizon_hours: float | None = None) -> tuple[list, dict]:
    """Return (events with h2h and btts merged, quota).

    Cost is 1 credit for match result across every fixture at once, plus
    1 credit per fixture for BTTS. BTTS is not served by the bulk /odds
    endpoint -- it returns HTTP 422 INVALID_MARKET -- and is only available
    per event. That is why this is not the flat 2 credits the original
    pre-registration assumed; see the 20 September 2026 amendment in
    spec/experiment-02-price-comparison.md.

    horizon_hours limits BTTS calls to fixtures kicking off within that
    many hours, so a capture does not spend a credit on every fixture in
    the next three matchweeks.
    """
    events, quota = _get(api_key, f"/v4/sports/{SPORT}/odds",
                         regions=REGIONS, markets="h2h",
                         oddsFormat="decimal", dateFormat="iso")
    spent = int(quota.get("last_request_cost") or 1)

    if horizon_hours is not None:
        cutoff = datetime.now(timezone.utc).timestamp() + horizon_hours * 3600
        wanted = [e for e in events
                  if datetime.fromisoformat(
                      e["commence_time"].replace("Z", "+00:00")).timestamp() <= cutoff]
    else:
        wanted = list(events)

    for ev in wanted:
        detail, q = _get(api_key, f"/v4/sports/{SPORT}/events/{ev['id']}/odds",
                         regions=REGIONS, markets="btts",
                         oddsFormat="decimal", dateFormat="iso")
        spent += int(q.get("last_request_cost") or 1)
        quota = q
        btts_by_key = {}
        for bm in detail.get("bookmakers", []):
            block = next((m for m in bm.get("markets", []) if m.get("key") == "btts"), None)
            if block is not None:
                btts_by_key[bm["key"]] = (bm, block)
        # Merge the BTTS block into the matching bookmaker on the h2h event,
        # matched on the API's stable key -- never on list position.
        existing = {bm["key"]: bm for bm in ev.get("bookmakers", [])}
        for key, (bm, block) in btts_by_key.items():
            if key in existing:
                existing[key].setdefault("markets", []).append(block)
            else:
                ev.setdefault("bookmakers", []).append(
                    {"key": key, "title": bm.get("title", key), "markets": [block]})

    quota["capture_cost_credits"] = spent
    quota["btts_fixtures_queried"] = len(wanted)
    return events, quota


def team_code(name: str) -> str:
    """the-odds-api club name -> the three-letter code used in fixture_ids."""
    table = {
        "Arsenal": "ARS", "Aston Villa": "AVL", "AFC Bournemouth": "BOU",
        "Bournemouth": "BOU", "Brentford": "BRE",
        "Brighton and Hove Albion": "BHA", "Brighton & Hove Albion": "BHA",
        "Chelsea": "CHE", "Coventry City": "COV", "Crystal Palace": "CRY",
        "Everton": "EVE", "Fulham": "FUL", "Hull City": "HUL",
        "Ipswich Town": "IPS", "Leeds United": "LEE", "Liverpool": "LIV",
        "Manchester City": "MCI", "Manchester United": "MUN",
        "Newcastle United": "NEW", "Nottingham Forest": "NFO",
        "Sunderland": "SUN", "Tottenham Hotspur": "TOT",
    }
    if name not in table:
        raise KeyError(f"unmapped club name {name!r} -- add it to team_code()")
    return table[name]


def _market_shape(market_key: str, home: str, away: str):
    """(outcome ids, labels, how to find each in the API's outcome list)."""
    if market_key == "h2h":
        return (["home_win", "draw", "away_win"],
                {"home_win": home, "draw": "Draw", "away_win": away},
                [home, "Draw", away])
    if market_key == "btts":
        return (["btts_yes", "btts_no"],
                {"btts_yes": "Yes", "btts_no": "No"},
                ["Yes", "No"])
    raise ValueError(f"unhandled market {market_key}")


def build_observations(events: list, slot: str, captured_at: str) -> list[dict]:
    out = []
    for ev in events:
        home, away = ev["home_team"], ev["away_team"]
        kickoff = ev["commence_time"]
        fixture_id = f"{kickoff[:10]}-{team_code(home)}-{team_code(away)}"

        for market_key, market_name in (("h2h", "match_result"), ("btts", "btts")):
            ids, labels, wanted = _market_shape(market_key, home, away)
            prices: dict[str, list[float]] = {}
            exchange_prices: dict[str, list[float]] = {}
            dropped: list[dict] = []

            affiliate_prices: dict[str, list[float]] = {}
            grouped: dict[str, dict[str, list[float]]] = {}

            for bm in ev.get("bookmakers", []):
                block = next((m for m in bm.get("markets", [])
                              if m.get("key") == market_key), None)
                if block is None:
                    continue
                by_name = {o["name"]: o["price"] for o in block.get("outcomes", [])}
                row = [by_name.get(w) for w in wanted]
                if any(p is None or p <= 1 for p in row):
                    # A partial row is dropped, loudly and on the record --
                    # never padded or guessed. This is the failure Experiment
                    # 01 could not see.
                    dropped.append({"bookmaker": bm.get("title", bm["key"]),
                                    "key": bm["key"],
                                    "reason": "incomplete or invalid prices",
                                    "raw": by_name})
                    continue

                key, title = bm["key"], bm.get("title", bm["key"])
                if key == SUBJECT_KEY:
                    prices[SUBJECT_TITLE] = row
                elif key in SUBJECT_AFFILIATES:
                    affiliate_prices[title] = row
                elif key in EXCHANGES:
                    exchange_prices[title] = row
                elif key in BOOK_GROUPS:
                    grouped.setdefault(BOOK_GROUPS[key], {})[title] = row
                else:
                    prices[title] = row

            # Each brand group contributes one quote: the per-outcome median
            # of its members. Members are preserved in group_members.
            group_members = {}
            for group, members in grouped.items():
                rows = list(members.values())
                prices[group] = [round(statistics.median(r[i] for r in rows), 4)
                                 for i in range(len(ids))]
                group_members[group] = members

            if SUBJECT_TITLE not in prices:
                dropped.append({"bookmaker": SUBJECT_TITLE, "key": SUBJECT_KEY,
                                "reason": "subject book absent from this capture"})

            out.append({
                "experiment": "02",
                "fixture_id": fixture_id,
                "fixture": f"{home} v {away}",
                "kickoff_utc": kickoff,
                "market": market_name,
                "capture_slot": slot,
                "captured_at_utc": captured_at,
                "source": "the-odds-api.com",
                "source_event_id": ev.get("id"),
                "outcomes": ids,
                "outcome_labels": labels,
                "prices": prices,
                # Benchmark B. Kept alongside, never merged into `prices`.
                "exchange_prices": exchange_prices,
                # Same operator as the subject (Entain). Recorded, never
                # blended -- see SUBJECT_AFFILIATES.
                "subject_affiliate_prices": affiliate_prices,
                # Which brands collapsed into each single group quote.
                "group_members": group_members,
                "bookmakers_not_read": dropped,
            })
    return out


def write(observations: list[dict], raw: list, quota: dict, slot: str,
          captured_at: str) -> Path:
    stamp = captured_at.replace(":", "").replace("-", "")[:15]
    day = captured_at[:10]
    raw_dir = EXPERIMENT / "observations" / "raw"
    obs_dir = EXPERIMENT / "observations"
    raw_dir.mkdir(parents=True, exist_ok=True)

    raw_path = raw_dir / f"{day}-{slot}-{stamp}.json"
    raw_path.write_text(json.dumps(
        {"captured_at_utc": captured_at, "capture_slot": slot,
         "quota": quota, "response": raw}, indent=2) + "\n")

    for obs in observations:
        name = f"{obs['fixture_id']}-{obs['market']}-{slot}-{stamp}.json"
        (obs_dir / name).write_text(json.dumps(obs, indent=2) + "\n")
    return raw_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slot", choices=SLOTS, required=False,
                    help="which scheduled capture this is (section 3)")
    ap.add_argument("--from-raw", metavar="FILE",
                    help="rebuild observations from a saved raw response; spends no credits")
    ap.add_argument("--horizon-hours", type=float, default=30.0,
                    help="only spend a BTTS credit on fixtures kicking off within "
                         "this many hours (default 30, i.e. the T-24h slot's own "
                         "matchweek and nothing beyond it)")
    args = ap.parse_args()

    if args.from_raw:
        saved = json.loads(Path(args.from_raw).read_text())
        raw = saved["response"]
        slot = args.slot or saved.get("capture_slot", "closing")
        captured_at = saved.get("captured_at_utc") or datetime.now(timezone.utc).isoformat()
        quota = saved.get("quota", {})
    else:
        if not args.slot:
            ap.error("--slot is required for a live capture")
        slot = args.slot
        raw, quota = fetch(load_api_key(), args.horizon_hours)
        captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    observations = build_observations(raw, slot, captured_at)
    raw_path = write(observations, raw, quota, slot, captured_at)

    fixtures = {o["fixture_id"] for o in observations}
    books = {b for o in observations for b in o["prices"]}
    no_subject = [o["fixture_id"] for o in observations
                  if SUBJECT_TITLE not in o["prices"]]

    print(f"capture {slot} at {captured_at}")
    print(f"  {len(fixtures)} fixture(s), {len(observations)} market observation(s)")
    print(f"  {len(books)} sportsbook(s) in consensus pool; "
          f"exchanges kept separate: "
          f"{sorted({e for o in observations for e in o['exchange_prices']})}")
    if no_subject:
        print(f"  NO {SUBJECT_TITLE} PRICE in: {sorted(set(no_subject))}")
    if quota.get("requests_remaining") is not None:
        print(f"  credits: this capture cost {quota.get('capture_cost_credits')} "
              f"(1 for match result across all fixtures + 1 each for BTTS on "
              f"{quota.get('btts_fixtures_queried')} fixture(s)); "
              f"{quota['requests_remaining']} remaining this month")
    print(f"  raw response -> {raw_path.relative_to(ROOT)}")
    print("\nNext: python3 scripts/price_screen.py "
          f"{(EXPERIMENT / 'observations').relative_to(ROOT)}/*-{slot}-*.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
