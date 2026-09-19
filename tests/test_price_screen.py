"""Tests for the Experiment 01 price screen.

Values here were verified empirically against the implementation before
being written down, not guessed. The borderline case at 4.30 is a real
method disagreement (proportional and two-lowest-margin clear 3%, Shin
does not), which is exactly the situation the pre-registration says must
be recorded as NOT qualifying.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from price_screen import (  # noqa: E402
    SUBJECT,
    THRESHOLD,
    consensus_median,
    fair_proportional,
    fair_shin,
    overround,
    screen_market,
)

# Four soft books plus one sharp low-margin book that prices the longshot
# materially shorter. Realistic shape: soft books drift longshots out.
SOFT_BOOKS = {
    "A": [2.00, 3.50, 4.00],
    "B": [2.02, 3.45, 3.95],
    "C": [1.98, 3.55, 4.05],
    "D": [2.00, 3.50, 4.00],
    "Sharp": [2.05, 3.55, 3.65],
}


def _market(ladbrokes_prices):
    prices = dict(SOFT_BOOKS)
    prices[SUBJECT] = ladbrokes_prices
    return {
        "fixture_id": "TEST-FIXTURE",
        "market": "match_result",
        "captured_at_utc": "2026-09-19T00:00:00Z",
        "outcomes": ["home_win", "draw", "away_win"],
        "prices": prices,
    }


def _away(result):
    return result["outcomes"][2]


def test_clearly_qualifying_case():
    """Ladbrokes well above consensus on the away outcome: all three agree."""
    away = _away(screen_market(_market([2.00, 3.50, 4.50])))
    assert away["qualifies"] is True
    assert away["method_sensitive"] is False
    assert away["edge_proportional"] >= THRESHOLD
    assert away["edge_shin"] >= THRESHOLD
    assert away["edge_two_lowest_margin"] >= THRESHOLD


def test_clearly_non_qualifying_case():
    """Ladbrokes shorter than consensus: every method returns a negative edge."""
    away = _away(screen_market(_market([2.00, 3.50, 4.10])))
    assert away["qualifies"] is False
    assert away["method_sensitive"] is False
    assert away["edge_proportional"] < 0
    assert away["edge_shin"] < 0
    assert away["edge_two_lowest_margin"] < 0


def test_method_sensitive_borderline_is_not_qualifying():
    """Proportional and two-lowest clear 3%; Shin does not.

    Pre-registration section 4: disagreement between reasonable methods is
    evidence of noise, so this must NOT qualify, and must be flagged.
    """
    away = _away(screen_market(_market([2.00, 3.50, 4.30])))
    assert away["edge_proportional"] >= THRESHOLD
    assert away["edge_two_lowest_margin"] >= THRESHOLD
    assert away["edge_shin"] < THRESHOLD
    assert away["qualifies"] is False, "method disagreement must not qualify"
    assert away["method_sensitive"] is True


def test_ladbrokes_is_excluded_from_its_own_benchmark():
    """The consensus must not move when only the subject book's price moves."""
    modest = screen_market(_market([2.00, 3.50, 4.10]))
    absurd = screen_market(_market([2.00, 3.50, 99.0]))

    modest_fair = [o["consensus_fair_price_proportional"] for o in modest["outcomes"]]
    absurd_fair = [o["consensus_fair_price_proportional"] for o in absurd["outcomes"]]
    assert modest_fair == absurd_fair, "Ladbrokes leaked into its own benchmark"

    assert SUBJECT not in modest["books_in_consensus"]
    assert modest["books_in_consensus_count"] == len(SOFT_BOOKS)


def test_consensus_ignores_subject_even_if_listed_first():
    """Ordering must not matter to exclusion."""
    prices = {SUBJECT: [2.00, 3.50, 9.00]}
    prices.update(SOFT_BOOKS)
    fair = consensus_median(prices, 3)
    fair_without = consensus_median(SOFT_BOOKS, 3)
    assert fair == fair_without


def test_books_with_incomplete_prices_are_dropped():
    prices = dict(SOFT_BOOKS)
    prices["Broken"] = [2.00, 3.50]          # wrong length
    prices["AlsoBroken"] = [2.00, None, 4.0]  # unusable value
    prices[SUBJECT] = [2.00, 3.50, 4.10]
    result = screen_market({
        "outcomes": ["home_win", "draw", "away_win"],
        "prices": prices,
    })
    assert "Broken" not in result["books_in_consensus"]
    assert "AlsoBroken" not in result["books_in_consensus"]
    assert result["books_in_consensus_count"] == len(SOFT_BOOKS)


def test_fair_probabilities_sum_to_one():
    """Both margin-removal methods must produce a coherent book."""
    prices = [2.00, 3.50, 4.00]
    assert abs(sum(fair_proportional(prices)) - 1.0) < 1e-9
    assert abs(sum(fair_shin(prices)) - 1.0) < 1e-6


def test_shin_shrinks_longshots_relative_to_proportional():
    """Sanity check that Shin is doing what Shin is supposed to do.

    Shin corrects favourite-longshot bias, so relative to proportional it
    hands the favourite MORE probability and longshots LESS. This needs a
    book with an actual margin -- see the zero-margin test below for why.
    """
    prices = [1.20, 7.00, 15.00]   # booksum ~1.043, a real margin
    prop = fair_proportional(prices)
    shin = fair_shin(prices)
    assert shin[0] > prop[0], "favourite should get more probability under Shin"
    assert shin[1] < prop[1], "mid-price should get less probability under Shin"
    assert shin[2] < prop[2], "longshot should get less probability under Shin"


def test_zero_margin_book_leaves_both_methods_identical():
    """A book with no overround has nothing to remove.

    Caught during development: [1.50, 4.50, 9.00] sums to exactly 1.0000,
    so Shin and proportional must agree exactly. Worth pinning down, since
    a degenerate input like this silently invalidates any test that expects
    the two methods to differ.
    """
    prices = [1.50, 4.50, 9.00]
    assert abs(overround(prices)) < 1e-9
    prop = fair_proportional(prices)
    shin = fair_shin(prices)
    for a, b in zip(prop, shin):
        assert abs(a - b) < 1e-9


def test_overround_is_positive_for_a_real_book():
    assert overround([2.00, 3.50, 4.00]) > 0


def test_two_outcome_market_works():
    """BTTS is a two-outcome market; the screen must handle it."""
    prices = {
        "A": [1.80, 2.00],
        "B": [1.83, 1.97],
        "C": [1.78, 2.05],
        SUBJECT: [1.80, 2.30],
    }
    result = screen_market({
        "outcomes": ["btts_yes", "btts_no"],
        "prices": prices,
    })
    assert len(result["outcomes"]) == 2
    assert result["outcomes"][1]["qualifies"] is True  # 2.30 vs ~2.0 consensus
