import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from edge_calculator import clv, edge, fair_probability, implied_probability, overround


def test_implied_probability():
    assert math.isclose(implied_probability(2.0), 0.5)


def test_overround_positive_for_real_market():
    # three-way market, each side priced with the bookmaker's margin baked in
    assert overround([2.10, 3.60, 3.80]) > 0


def test_fair_probability_removes_the_margin():
    market = [2.10, 3.60, 3.80]
    fp = fair_probability(2.10, market)
    assert fp < implied_probability(2.10)


def test_edge_is_our_probability_minus_fair_probability():
    market = [2.10, 3.60, 3.80]
    e = edge(0.55, 2.10, market)
    assert math.isclose(e, 0.55 - fair_probability(2.10, market))


def test_clv_positive_when_price_obtained_beats_closing_price():
    # obtained longer odds (2.10) than the market closed at (1.95) -> good CLV
    assert clv(price_obtained=2.10, closing_price=1.95) > 0


def test_clv_negative_when_closing_price_was_better():
    # market drifted the other way -> obtained price was worse than close
    assert clv(price_obtained=1.80, closing_price=1.95) < 0
