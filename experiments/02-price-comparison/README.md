# Experiment 02 — price comparison, API edition

Pre-registration: [`spec/experiment-02-price-comparison.md`](../../spec/experiment-02-price-comparison.md).
Supersedes Experiment 01, halted for a measurement fault
([`../01-price-comparison/HALTED.md`](../01-price-comparison/HALTED.md)).

**Status: built, not started.** Nothing has been collected. Collection
cannot begin until an `ODDS_API_KEY` exists — free Starter tier at
the-odds-api.com, 500 credits/month, of which this needs about 80 for
the full eight weeks.

## Running a capture

```bash
python3 scripts/collect_odds.py --slot T-24h    # costs 2 credits
python3 scripts/price_screen.py experiments/02-price-comparison/observations/*-T-24h-*.json
```

Slots, per section 3 of the pre-registration: `T-24h`, `T-3h`, `T-1h`,
`T-15m`, `closing`. Five per matchweek. The raw API response is written
to `observations/raw/` before anything is derived from it, and every
capture is committed — including the ones where nothing qualifies,
which should be almost all of them.

`--from-raw <file>` rebuilds observations from a saved raw response and
spends no credits. Use it for anything that isn't a fresh capture.

## What the collector guarantees

Experiment 01 died because a price could be attributed to the wrong
bookmaker with nothing visibly going wrong. The tests in
`tests/test_collect_odds.py` assert that specific failure cannot recur:

- a bookmaker missing any outcome is **dropped and recorded**, never
  shifted or padded;
- the subject book is matched on the API's stable `ladbrokes_uk` key,
  not on a display name or a column position;
- exchange prices (Betfair Exchange, Matchbook, Smarkets) are kept in a
  separate `exchange_prices` field and can never reach the consensus
  pool — Benchmark B, section 4;
- an unmapped club name raises rather than guessing;
- BTTS is captured, which it never was in Experiment 01.

Run them with `python3 tests/run.py`.

## What would make this stop

Section 10 of the pre-registration, written before any data: four
conditions, all of which must hold to justify a real-money trial. If any
one fails the answer is no, and this project stops looking for edge in
retail football betting. Both analysts expect that outcome.

**No money is staked on anything arising from this experiment while it
runs.**
