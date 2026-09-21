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


# --------------------------------------------------------------------------
# Pre-flight findings, 20 September 2026. Each of these is a real property
# of the-odds-api's UK feed, observed before any data was collected.
# --------------------------------------------------------------------------

def test_coral_is_excluded_from_the_consensus():
    """Coral and Ladbrokes are both Entain and quote near-identically.

    Fulham v Man Utd, 20 Sept 2026: both at exactly 1.50/2.45 on BTTS.
    Leaving Coral in would measure Ladbrokes partly against itself.
    """
    o = build([
        book("ladbrokes_uk", "Ladbrokes", h2h=[3.4, 3.7, 2.0]),
        book("coral", "Coral", h2h=[3.4, 3.7, 2.05]),
        book("williamhill", "William Hill", h2h=[3.4, 3.6, 2.0]),
    ])
    assert set(o["prices"]) == {"Ladbrokes", "William Hill"}
    assert o["subject_affiliate_prices"] == {"Coral": [3.4, 3.7, 2.05]}


def test_same_product_under_two_brands_gets_one_vote():
    """LiveScore Bet and Virgin Bet quote identically; one desk, one vote."""
    o = build([
        book("ladbrokes_uk", "Ladbrokes", h2h=[3.4, 3.7, 2.0]),
        book("livescorebet", "LiveScore Bet", h2h=[3.6, 3.65, 1.93]),
        book("virginbet", "Virgin Bet", h2h=[3.6, 3.65, 1.93]),
        book("williamhill", "William Hill", h2h=[3.4, 3.6, 2.0]),
    ])
    assert "LiveScore Bet" not in o["prices"]
    assert "Virgin Bet" not in o["prices"]
    assert o["prices"]["LiveScore Group"] == [3.6, 3.65, 1.93]
    # both members preserved, nothing thrown away
    assert set(o["group_members"]["LiveScore Group"]) == {"LiveScore Bet", "Virgin Bet"}


def test_group_quote_is_the_median_when_members_disagree():
    o = build([
        book("ladbrokes_uk", "Ladbrokes", h2h=[3.4, 3.7, 2.0]),
        book("livescorebet", "LiveScore Bet", h2h=[3.6, 3.6, 1.90]),
        book("virginbet", "Virgin Bet", h2h=[3.4, 3.7, 2.00]),
    ])
    assert o["prices"]["LiveScore Group"] == [3.5, 3.65, 1.95]


def test_all_three_exchanges_stay_out():
    """Betfair, Matchbook and Smarkets all quoted 3.70/3.95/~2.06 -- blending
    them would have put three near-identical exchange quotes in the median."""
    o = build([
        book("ladbrokes_uk", "Ladbrokes", h2h=[3.4, 3.7, 2.0]),
        book("betfair_ex_uk", "Betfair", h2h=[3.7, 3.95, 2.06]),
        book("matchbook", "Matchbook", h2h=[3.7, 3.95, 2.06]),
        book("smarkets", "Smarkets", h2h=[3.7, 3.95, 2.04]),
        book("williamhill", "William Hill", h2h=[3.4, 3.6, 2.0]),
    ])
    assert set(o["prices"]) == {"Ladbrokes", "William Hill"}
    assert set(o["exchange_prices"]) == {"Betfair", "Matchbook", "Smarkets"}


def test_excluded_books_never_reach_the_screen():
    o = build([
        book("ladbrokes_uk", "Ladbrokes", h2h=[3.4, 3.7, 2.0]),
        book("coral", "Coral", h2h=[3.4, 3.7, 2.05]),
        book("betfair_ex_uk", "Betfair", h2h=[3.7, 3.95, 2.06]),
        book("livescorebet", "LiveScore Bet", h2h=[3.6, 3.65, 1.93]),
        book("virginbet", "Virgin Bet", h2h=[3.6, 3.65, 1.93]),
        book("williamhill", "William Hill", h2h=[3.4, 3.6, 2.0]),
        book("betfred_uk", "Betfred (UK)", h2h=[3.4, 3.75, 2.0]),
    ])
    screened = ps.screen_market(o)
    assert screened["books_in_consensus"] == [
        "Betfred (UK)", "LiveScore Group", "William Hill"]


# --------------------------------------------------------------------------
# Era 02 CLV scoring. Verified against the Matchweek 4 figures computed
# independently on 21 September: -0.75, -0.81 and -0.78 EV per £10.
# --------------------------------------------------------------------------

import clv_score  # noqa: E402


def _table():
    return clv_score.closing_table()


def test_clv_reproduces_the_matchweek_4_expected_values():
    table = _table()
    cases = [
        ("2026-09-13-COV-BHA", "draw", 3.70, -0.75),
        ("2026-09-14-LEE-NEW", "away_win", 2.90, -0.81),
        ("2026-09-13-MUN-MCI", "away_win", 2.15, -0.78),
    ]
    for fid, sel, price, expected_ev in cases:
        e = {"fixture_id": fid, "selection": sel, "decision_price": price}
        assert clv_score.score(e, table), f"{fid} not found in closing data"
        assert abs(e["ev_per_10_gbp"] - expected_ev) < 0.02, (
            f"{fid}: got {e['ev_per_10_gbp']}, expected {expected_ev}")
        assert e["clv_pp"] < 0, f"{fid} should have negative CLV"


def test_closing_price_is_margin_removed_not_raw():
    table = _table()
    e = {"fixture_id": "2026-09-14-LEE-NEW", "selection": "away_win",
         "decision_price": 2.90}
    clv_score.score(e, table)
    assert e["closing_price"] == 2.98          # raw close
    assert e["closing_fair_price"] > 3.1       # margin removed, longer
    assert 0.05 < e["closing_overround"] < 0.07


def test_a_price_better_than_the_fair_close_scores_positive():
    """The whole point: CLV is positive when you beat the fair closing price."""
    table = _table()
    e = {"fixture_id": "2026-09-14-LEE-NEW", "selection": "away_win",
         "decision_price": 3.60}     # better than the 3.16 fair close
    clv_score.score(e, table)
    assert e["clv_pp"] > 0
    assert e["ev_per_10_gbp"] > 0


def test_unknown_fixture_is_left_unscored_rather_than_guessed():
    e = {"fixture_id": "2027-01-01-ARS-LIV", "selection": "home_win",
         "decision_price": 2.0}
    assert clv_score.score(e, _table()) is False
    assert "clv_pp" not in e


def test_btts_is_left_unscored_until_a_source_exists():
    """The season CSV has no BTTS closing column. Null, never invented."""
    e = {"fixture_id": "2026-09-14-LEE-NEW", "selection": "btts_no",
         "decision_price": 2.0}
    assert clv_score.score(e, _table()) is False
