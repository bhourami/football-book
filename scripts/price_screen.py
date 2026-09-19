#!/usr/bin/env python3
"""Experiment 01 price screen — spec/experiment-01-price-comparison.md.

Answers one question per outcome: does Ladbrokes offer at least 3% more
than the wider market's margin-adjusted consensus fair price?

Deliberately contains no forecasting model, no probability estimate of our
own, and no opinion about who will win. It compares prices only.

Three margin-removal methods are computed. A selection qualifies only when
ALL THREE agree it clears the threshold (pre-registration section 4). Where
they disagree, the selection is recorded as NOT qualifying and flagged
method_sensitive -- disagreement between reasonable methods is evidence of
noise, not of opportunity.

No external dependencies.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

SUBJECT = "Ladbrokes"          # the book under measurement
THRESHOLD = 0.03               # pre-registered, section 5. Do not tune.


# --------------------------------------------------------------------------
# margin removal
# --------------------------------------------------------------------------

def implied_probabilities(prices: list[float]) -> list[float]:
    for p in prices:
        if p <= 1:
            raise ValueError(f"decimal odds must be > 1, got {p}")
    return [1 / p for p in prices]


def booksum(prices: list[float]) -> float:
    """Sum of implied probabilities. Equals 1 + overround."""
    return sum(implied_probabilities(prices))


def overround(prices: list[float]) -> float:
    return booksum(prices) - 1


def fair_proportional(prices: list[float]) -> list[float]:
    """Proportional margin removal, matching scripts/edge_calculator.py."""
    ov = overround(prices)
    return [p / (1 + ov) for p in implied_probabilities(prices)]


def fair_shin(prices: list[float]) -> list[float]:
    """Shin (1993) margin removal.

    Models the book's margin as protection against insider traders holding
    a fraction z of the money, and shrinks longshots harder than the
    proportional method does. z is solved numerically so the fair
    probabilities sum to 1.
    """
    pis = implied_probabilities(prices)
    bs = sum(pis)
    if bs <= 1.0:
        # No margin to remove (or a mispriced/arbitrage book). Normalise.
        return [pi / bs for pi in pis]

    def probs_at(z: float) -> list[float]:
        out = []
        for pi in pis:
            inner = z * z + 4 * (1 - z) * (pi * pi) / bs
            out.append((math.sqrt(inner) - z) / (2 * (1 - z)))
        return out

    lo, hi = 0.0, 0.9999
    for _ in range(200):
        mid = (lo + hi) / 2
        if sum(probs_at(mid)) > 1.0:
            lo = mid
        else:
            hi = mid
    return probs_at((lo + hi) / 2)


# --------------------------------------------------------------------------
# consensus
# --------------------------------------------------------------------------

def _usable_books(prices_by_book: dict[str, list[float]], n_outcomes: int) -> dict[str, list[float]]:
    """Drop the subject book, and any book with incomplete or invalid prices.

    Excluding Ladbrokes is pre-registration section 4 step 2: the book being
    measured must not contribute to the benchmark it is measured against.
    """
    usable = {}
    for book, prices in prices_by_book.items():
        if book == SUBJECT:
            continue
        if prices is None or len(prices) != n_outcomes:
            continue
        if any((p is None or p <= 1) for p in prices):
            continue
        usable[book] = list(prices)
    return usable


def consensus_median(prices_by_book: dict[str, list[float]], n_outcomes: int,
                     method: str = "proportional") -> list[float]:
    """Median fair probability per outcome across books (section 4 step 4)."""
    books = _usable_books(prices_by_book, n_outcomes)
    if not books:
        raise ValueError("no usable books for consensus")
    fair_fn = fair_proportional if method == "proportional" else fair_shin
    per_book = [fair_fn(p) for p in books.values()]
    return [statistics.median([fb[i] for fb in per_book]) for i in range(n_outcomes)]


def consensus_two_lowest_margin(prices_by_book: dict[str, list[float]],
                                n_outcomes: int) -> list[float]:
    """Sensitivity check: consensus from only the two lowest-overround books."""
    books = _usable_books(prices_by_book, n_outcomes)
    if len(books) < 2:
        raise ValueError("need at least two usable books for the low-margin check")
    ranked = sorted(books.items(), key=lambda kv: overround(kv[1]))[:2]
    per_book = [fair_proportional(p) for _, p in ranked]
    return [statistics.median([fb[i] for fb in per_book]) for i in range(n_outcomes)]


# --------------------------------------------------------------------------
# the screen
# --------------------------------------------------------------------------

def screen_market(observation: dict) -> dict:
    """Apply the pre-registered rule to one market observation."""
    outcomes = observation["outcomes"]
    prices_by_book = observation["prices"]
    n = len(outcomes)

    if SUBJECT not in prices_by_book:
        raise ValueError(f"observation has no {SUBJECT} price; nothing to measure")
    subject_prices = prices_by_book[SUBJECT]
    if len(subject_prices) != n:
        raise ValueError(f"{SUBJECT} price list does not match outcomes")

    usable = _usable_books(prices_by_book, n)

    fair_prop = consensus_median(prices_by_book, n, "proportional")
    fair_shin_ = consensus_median(prices_by_book, n, "shin")
    fair_low = consensus_two_lowest_margin(prices_by_book, n)

    results = []
    for i, outcome in enumerate(outcomes):
        lad = subject_prices[i]
        edges = {}
        for label, fair_probs in (("proportional", fair_prop),
                                  ("shin", fair_shin_),
                                  ("two_lowest_margin", fair_low)):
            fair_price = 1 / fair_probs[i]
            edges[label] = (lad / fair_price) - 1

        clears = {k: (v >= THRESHOLD) for k, v in edges.items()}
        all_clear = all(clears.values())
        any_clear = any(clears.values())

        results.append({
            "outcome": outcome,
            "ladbrokes_price": lad,
            "consensus_fair_price_proportional": round(1 / fair_prop[i], 4),
            "edge_proportional": round(edges["proportional"], 5),
            "edge_shin": round(edges["shin"], 5),
            "edge_two_lowest_margin": round(edges["two_lowest_margin"], 5),
            "qualifies": all_clear,
            # Disagreement between methods => not qualifying, and flagged.
            "method_sensitive": any_clear and not all_clear,
        })

    return {
        "fixture_id": observation.get("fixture_id"),
        "market": observation.get("market"),
        "captured_at_utc": observation.get("captured_at_utc"),
        "books_in_consensus": sorted(usable.keys()),
        "books_in_consensus_count": len(usable),
        "books_excluded_or_unreadable": observation.get("bookmakers_not_read", []),
        "threshold": THRESHOLD,
        "outcomes": results,
    }


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", help="observation JSON file(s)")
    ap.add_argument("--quiet", action="store_true",
                    help="print only qualifying selections and the summary")
    args = ap.parse_args()

    screened = 0
    qualifying = 0
    sensitive = 0
    all_out = []

    for path in args.files:
        obs = json.loads(Path(path).read_text())
        res = screen_market(obs)
        all_out.append(res)
        for o in res["outcomes"]:
            screened += 1
            if o["qualifies"]:
                qualifying += 1
            if o["method_sensitive"]:
                sensitive += 1
        if not args.quiet:
            print(json.dumps(res, indent=2))
        else:
            for o in res["outcomes"]:
                if o["qualifies"]:
                    print(f"QUALIFIES  {res['fixture_id']}  {res['market']}  "
                          f"{o['outcome']}  Lad {o['ladbrokes_price']}  "
                          f"edge {o['edge_proportional']:+.3%}")

    print(json.dumps({
        "markets_screened": len(all_out),
        "outcomes_screened": screened,
        "qualifying": qualifying,
        "qualifying_rate": round(qualifying / screened, 4) if screened else None,
        "method_sensitive": sensitive,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
