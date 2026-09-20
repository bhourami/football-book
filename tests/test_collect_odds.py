"""Tests for the Experiment 02 collector.

The point of these is narrow and specific: Experiment 01 was halted
because a price could be attributed to the wrong bookmaker without
anything visibly going wrong. These assert that cannot happen here --
that a partial row is dropped rather than shifted or padded, that the
subject book is identified by API key rather than by position, and that
exchange prices never reach the consensus pool.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import collect_odds as c  # noqa: E402
import price_screen as ps  # noqa: E402


def event(bookmakers):
    return {
        "id": "evt1",
        "home_team": "Bournemouth",
        "away_team": "Liverpool",
        "commence_time": "2026-09-20T13:00:00Z",
        "bookmakers": bookmakers,
    }


def book(key, title, h2h=None, btts=None):
    markets = []
    if h2h:
        markets.append({"key": "h2h", "outcomes": [
            {"name": "Bournemouth", "price": h2h[0]},
            {"name": "Draw", "price": h2h[1]},
            {"name": "Liverpool", "price": h2h[2]}]})
    if btts:
        markets.append({"key": "btts", "outcomes": [
            {"name": "Yes", "price": btts[0]},
            {"name": "No", "price": btts[1]}]})
    return {"key": key, "title": title, "markets": markets}


def build(bookmakers, market="match_result"):
    obs = c.build_observations([event(bookmakers)], "T-24h", "2026-09-19T12:00:00Z")
    return next(o for o in obs if o["market"] == market)


def test_fixture_id_uses_kickoff_date_and_club_codes():
    o = build([book("ladbrokes_uk", "Ladbrokes", h2h=[3.1, 3.75, 2.1])])
    assert o["fixture_id"] == "2026-09-20-BOU-LIV"


def test_subject_identified_by_api_key_not_display_title():
    # the-odds-api's title for the subject could change; the key is stable.
    o = build([book("ladbrokes_uk", "Ladbrokes Coral", h2h=[3.1, 3.75, 2.1])])
    assert "Ladbrokes" in o["prices"]
    assert o["prices"]["Ladbrokes"] == [3.1, 3.75, 2.1]


def test_exchanges_are_never_in_the_consensus_pool():
    o = build([
        book("ladbrokes_uk", "Ladbrokes", h2h=[3.1, 3.75, 2.1]),
        book("betfair_ex_uk", "Betfair Exchange", h2h=[3.2, 3.9, 2.16]),
        book("matchbook", "Matchbook", h2h=[3.15, 3.85, 2.14]),
        book("williamhill", "William Hill", h2h=[3.0, 3.6, 2.15]),
    ])
    assert set(o["prices"]) == {"Ladbrokes", "William Hill"}
    assert set(o["exchange_prices"]) == {"Betfair Exchange", "Matchbook"}


def test_partial_row_is_dropped_not_shifted():
    """The Experiment 01 failure mode, asserted against directly."""
    partial = book("williamhill", "William Hill", h2h=[3.0, 3.6, 2.15])
    partial["markets"][0]["outcomes"].pop(1)  # draw price missing
    o = build([book("ladbrokes_uk", "Ladbrokes", h2h=[3.1, 3.75, 2.1]), partial])
    assert "William Hill" not in o["prices"]
    dropped = [d["bookmaker"] for d in o["bookmakers_not_read"]]
    assert "William Hill" in dropped
    # and critically: nothing shifted into the gap
    assert o["prices"]["Ladbrokes"] == [3.1, 3.75, 2.1]


def test_invalid_price_is_dropped():
    o = build([book("ladbrokes_uk", "Ladbrokes", h2h=[3.1, 3.75, 2.1]),
               book("betfred", "Betfred", h2h=[3.0, 1.0, 2.15])])
    assert "Betfred" not in o["prices"]


def test_missing_subject_is_recorded_loudly():
    o = build([book("williamhill", "William Hill", h2h=[3.0, 3.6, 2.15])])
    assert "Ladbrokes" not in o["prices"]
    reasons = [d["reason"] for d in o["bookmakers_not_read"]]
    assert any("subject book absent" in r for r in reasons)


def test_btts_market_is_captured():
    """BTTS was half of Experiment 01's scope and 0% of its data."""
    o = build([book("ladbrokes_uk", "Ladbrokes", btts=[1.8, 2.0]),
               book("williamhill", "William Hill", btts=[1.75, 2.05])],
              market="btts")
    assert o["outcomes"] == ["btts_yes", "btts_no"]
    assert o["prices"]["Ladbrokes"] == [1.8, 2.0]


def test_output_feeds_price_screen_unmodified():
    """The collector's observation must be what the screen already reads."""
    o = build([
        book("ladbrokes_uk", "Ladbrokes", h2h=[3.1, 3.75, 2.1]),
        book("williamhill", "William Hill", h2h=[3.0, 3.6, 2.15]),
        book("betfred", "Betfred", h2h=[3.0, 3.75, 2.15]),
        book("betfair_ex_uk", "Betfair Exchange", h2h=[3.3, 4.0, 2.2]),
    ])
    screened = ps.screen_market(o)
    assert screened["books_in_consensus"] == ["Betfred", "William Hill"]
    assert "Betfair Exchange" not in screened["books_in_consensus"]
    assert len(screened["outcomes"]) == 3
    for row in screened["outcomes"]:
        assert row["qualifies"] is False   # nothing here clears 3% on all methods


def test_unmapped_club_name_raises_rather_than_guessing():
    ev = event([book("ladbrokes_uk", "Ladbrokes", h2h=[3.1, 3.75, 2.1])])
    ev["home_team"] = "Wrexham"
    try:
        c.build_observations([ev], "T-24h", "2026-09-19T12:00:00Z")
    except KeyError as exc:
        assert "Wrexham" in str(exc)
    else:
        raise AssertionError("expected KeyError for an unmapped club")
