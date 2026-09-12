#!/usr/bin/env python3
"""Edge and CLV arithmetic from spec/methodology.md sections 7 and 10.

No external dependencies. Pure functions plus a small CLI for one-off checks
at selection time.
"""
from __future__ import annotations

import argparse
import json
import sys


def implied_probability(decimal_odds: float) -> float:
    if decimal_odds <= 1:
        raise ValueError("decimal odds must be > 1")
    return 1 / decimal_odds


def overround(market_decimal_odds: list[float]) -> float:
    return sum(implied_probability(o) for o in market_decimal_odds) - 1


def fair_probability(decimal_odds: float, market_decimal_odds: list[float]) -> float:
    """Proportional method: strip the overround out of one runner's implied
    probability using the full market's overround."""
    ov = overround(market_decimal_odds)
    return implied_probability(decimal_odds) / (1 + ov)


def edge(our_probability: float, decimal_odds: float, market_decimal_odds: list[float]) -> float:
    return our_probability - fair_probability(decimal_odds, market_decimal_odds)


def required_strike_rate(decimal_odds: float, market_decimal_odds: list[float]) -> float:
    """Equals fair_probability; named separately for selection-card readability."""
    return fair_probability(decimal_odds, market_decimal_odds)


def clv(price_obtained: float, closing_price: float) -> float:
    """Difference in implied probability between the closing price and the
    price obtained. Positive means you beat the close (you got longer odds,
    i.e. lower implied probability, than the market settled on) —
    methodology section 10."""
    return implied_probability(closing_price) - implied_probability(price_obtained)


def _cli() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("edge", help="compute edge for one selection")
    s.add_argument("--our-probability", type=float, required=True)
    s.add_argument("--price", type=float, required=True, help="decimal odds obtained")
    s.add_argument("--market-odds", type=float, nargs="+", required=True,
                    help="decimal odds for every runner in the market, including --price")

    c = sub.add_parser("clv", help="compute closing line value for a settled/priced bet")
    c.add_argument("--price-obtained", type=float, required=True)
    c.add_argument("--closing-price", type=float, required=True)

    args = p.parse_args()

    if args.cmd == "edge":
        ov = overround(args.market_odds)
        fp = fair_probability(args.price, args.market_odds)
        e = args.our_probability - fp
        result = {
            "implied_probability": implied_probability(args.price),
            "overround": ov,
            "fair_probability": fp,
            "required_strike_rate": fp,
            "our_probability": args.our_probability,
            "edge": e,
        }
        print(json.dumps(result, indent=2))

    elif args.cmd == "clv":
        result = {
            "price_obtained_implied": implied_probability(args.price_obtained),
            "closing_price_implied": implied_probability(args.closing_price),
            "clv": clv(args.price_obtained, args.closing_price),
            "beat_close": clv(args.price_obtained, args.closing_price) > 0,
        }
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    sys.exit(_cli() or 0)
