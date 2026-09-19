#!/usr/bin/env python3
"""Walk-forward backtest of the Dixon-Coles model against Bet365 prices.

The central question: does the model beat the closing line?

Design, and its honest limits:

- Predictions begin once a full season of history exists, so the test set is
  2023-24 onward (~1,180 matches). The model is refit on everything strictly
  before each fixture -- no lookahead.
- Refitting happens every REFIT_EVERY matches rather than every single match,
  warm-started from the previous fit. Pure-Python speed compromise; stated
  rather than hidden.
- Selections are struck at the OPENING Bet365 price and CLV is measured
  against the CLOSING Bet365 price. Opening and closing differ in ~85% of
  matches, so this is a real CLV test, not a tautology.
- football-data.co.uk carries no BTTS market price. BTTS therefore cannot be
  tested for edge or CLV against a market. It CAN be tested for calibration
  against reality -- which is the sharper question for the bias that prompted
  this work.
"""
from __future__ import annotations

import sys
from collections import defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])

from fetch_data import load_all  # noqa: E402
from model import DixonColes, fair_probabilities  # noqa: E402

REFIT_EVERY = 10
EDGE_THRESHOLD = 0.03  # methodology.md section 7
STAKE = 10.0
TEST_FROM_SEASON = "2324"


def bucket_calibration(pairs, edges=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.01)):
    """pairs: list of (predicted_prob, outcome_bool)."""
    out = []
    for lo, hi in zip(edges, edges[1:]):
        sel = [(p, o) for p, o in pairs if lo <= p < hi]
        if not sel:
            continue
        pred = sum(p for p, _ in sel) / len(sel)
        actual = sum(1 for _, o in sel if o) / len(sel)
        out.append((lo, hi, len(sel), pred, actual))
    return out


def main():
    matches = load_all()
    test_start = next(i for i, m in enumerate(matches) if m["season"] >= TEST_FROM_SEASON)
    print(f"total matches {len(matches)}, test set from index {test_start} "
          f"({matches[test_start]['date'].date()}) -> {len(matches) - test_start} predictions\n")

    model = DixonColes()
    mr_cal, btts_cal = [], []
    selections = []
    n_pred = 0

    for i in range(test_start, len(matches)):
        m = matches[i]
        if not all([m["oh"], m["od"], m["oa"], m["ch"], m["cd"], m["ca"]]):
            continue

        if (i - test_start) % REFIT_EVERY == 0:
            warm = model.n_matches > 0
            model.fit(matches[:i], ref_date=m["date"],
                      iters=60 if warm else 250, lr=0.05)

        p = model.predict(m["home"], m["away"])
        n_pred += 1

        hg, ag = m["hg"], m["ag"]
        outcomes = {"home_win": hg > ag, "draw": hg == ag, "away_win": hg < ag}
        btts_actual = hg >= 1 and ag >= 1

        for k in ("home_win", "draw", "away_win"):
            mr_cal.append((p[k], outcomes[k]))
        btts_cal.append((p["btts_yes"], btts_actual))

        open_fair = dict(zip(("home_win", "draw", "away_win"),
                             fair_probabilities([m["oh"], m["od"], m["oa"]])))
        close_fair = dict(zip(("home_win", "draw", "away_win"),
                              fair_probabilities([m["ch"], m["cd"], m["ca"]])))
        open_price = {"home_win": m["oh"], "draw": m["od"], "away_win": m["oa"]}

        # One candidate per market: the highest-edge outcome, per project convention.
        best = max(("home_win", "draw", "away_win"), key=lambda k: p[k] - open_fair[k])
        edge = p[best] - open_fair[best]
        if edge >= EDGE_THRESHOLD:
            won = outcomes[best]
            pl = STAKE * (open_price[best] - 1) if won else -STAKE
            # CLV in implied-probability terms: positive means the price taken
            # was longer than the closing price (we beat the close).
            clv = close_fair[best] - open_fair[best]
            selections.append({
                "date": m["date"], "match": f"{m['home']} v {m['away']}",
                "pick": best, "edge": edge, "price": open_price[best],
                "won": won, "pl": pl, "clv": clv,
            })

    # ---------------- report ----------------
    print(f"predictions made: {n_pred}\n")

    print("=" * 66)
    print("MATCH RESULT CALIBRATION (all three outcomes pooled)")
    print("=" * 66)
    print(f"{'bucket':>12} {'n':>6} {'predicted':>10} {'actual':>9} {'gap':>8}")
    for lo, hi, n, pred, act in bucket_calibration(mr_cal):
        print(f"{lo:.1f}-{hi:.1f}{'':>4} {n:>6} {pred:>10.3f} {act:>9.3f} {act - pred:>+8.3f}")
    mr_mean_pred = sum(p for p, _ in mr_cal) / len(mr_cal)
    mr_mean_act = sum(1 for _, o in mr_cal if o) / len(mr_cal)
    print(f"{'OVERALL':>12} {len(mr_cal):>6} {mr_mean_pred:>10.3f} {mr_mean_act:>9.3f} "
          f"{mr_mean_act - mr_mean_pred:>+8.3f}")

    print()
    print("=" * 66)
    print("BTTS CALIBRATION (model P(both score) vs what actually happened)")
    print("=" * 66)
    print(f"{'bucket':>12} {'n':>6} {'predicted':>10} {'actual':>9} {'gap':>8}")
    for lo, hi, n, pred, act in bucket_calibration(btts_cal):
        print(f"{lo:.1f}-{hi:.1f}{'':>4} {n:>6} {pred:>10.3f} {act:>9.3f} {act - pred:>+8.3f}")
    b_pred = sum(p for p, _ in btts_cal) / len(btts_cal)
    b_act = sum(1 for _, o in btts_cal if o) / len(btts_cal)
    print(f"{'OVERALL':>12} {len(btts_cal):>6} {b_pred:>10.3f} {b_act:>9.3f} {b_act - b_pred:>+8.3f}")
    print(f"\nmean model P(BTTS yes) = {b_pred:.4f}")
    print(f"realised BTTS yes rate = {b_act:.4f}")
    print(f"bias = {b_pred - b_act:+.4f}  (negative => model systematically UNDER-predicts BTTS yes)")

    print()
    print("=" * 66)
    print(f"SELECTIONS AT THE {EDGE_THRESHOLD:.0%} EDGE THRESHOLD (struck at opening price)")
    print("=" * 66)
    if not selections:
        print("no selections met the threshold")
        return
    n = len(selections)
    wins = sum(1 for s in selections if s["won"])
    pl = sum(s["pl"] for s in selections)
    staked = n * STAKE
    clvs = [s["clv"] for s in selections]
    beat = sum(1 for c in clvs if c > 0)
    print(f"selections:        {n}  ({n / n_pred:.1%} of matches)")
    print(f"won:               {wins}  ({wins / n:.1%})")
    print(f"staked:            £{staked:,.0f}")
    print(f"P/L:               £{pl:+,.2f}   ROI {pl / staked:+.2%}")
    print(f"beat closing line: {beat}/{n}  ({beat / n:.1%})")
    print(f"mean CLV:          {sum(clvs) / n:+.4f}  (implied-probability points)")
    by_pick = defaultdict(list)
    for s in selections:
        by_pick[s["pick"]].append(s)
    print("\nby selection type:")
    for k, v in sorted(by_pick.items()):
        p_l = sum(x["pl"] for x in v)
        c = sum(x["clv"] for x in v) / len(v)
        w = sum(1 for x in v if x["won"])
        print(f"  {k:<10} n={len(v):<4} won={w:<4} P/L £{p_l:+9.2f}  "
              f"ROI {p_l / (len(v) * STAKE):+7.2%}  meanCLV {c:+.4f}")


if __name__ == "__main__":
    main()
