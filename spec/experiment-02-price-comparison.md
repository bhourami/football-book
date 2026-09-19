# Experiment 02 — Is Ladbrokes mispriced against the market? (API edition)

**Pre-registration. Written and committed 19 September 2026, BEFORE any
data was collected under this design.** Supersedes Experiment 01, which
was halted for a measurement fault (see
`experiments/01-price-comparison/HALTED.md`). Same rules as before: once
collection begins, nothing here changes. A design flaw means halting and
re-registering as Experiment 03, with the reason recorded.

---

## 1. What changed from Experiment 01, and why

Experiment 01 asked the right question with the wrong instrument. Prices
were scraped from a rendered HTML grid that silently mis-attributes
columns when a cell is blank — a failure mode that *manufactures false
opportunities*, which is fatal for an experiment designed to find none.

Experiment 02 keeps the question and the discipline, and replaces the
instrument with a structured odds API (`the-odds-api.com`). Each price
arrives as a labelled JSON field attached to a named bookmaker. Column
alignment cannot silently fail because there are no columns.

Three further improvements this makes possible:

- **BTTS becomes capturable** (`btts` market key). It was half of
  Experiment 01's registered scope and 0% of its collected data.
- **Automated repeat capture** makes the survival test real rather than
  manual, and raises sample size enough for the decision rule to mean
  something.
- **True closing line value becomes measurable** — see section 8. This
  fixes a metric the project has so far been computing wrongly.

## 2. The question

Unchanged from Experiment 01: **does Ladbrokes, the bookmaker actually
used, sometimes offer a price materially better than the wider market's
margin-adjusted consensus — and does it survive long enough to place by
hand?**

No forecasting model. No probability estimate of our own. This is a
price-comparison question, which is why the BTTS pause in
`methodology.md` section 7 does not apply to it: that pause bars BTTS
selections derived from *our model*, and this experiment has no model.

**H0, expected: it does not**, or qualifying instances are too rare, too
short-lived, or too method-sensitive to act on. Most capture rounds
should return zero. A round returning many is treated as a suspected
fault first and investigated before being recorded as a result.

## 3. Universe and capture

- Competition: Premier League (`soccer_epl`).
- Markets: `h2h` (match result) and `btts`.
- Region: `uk`.
- Every fixture returned by the endpoint. No discretionary selection.
- Capture schedule: **T-24h, T-3h, T-1h, and T-15m before each kickoff**,
  plus one capture as close to kickoff as the schedule permits, which
  serves as the closing-price reference (section 8).
- Every capture is stored raw and committed. Nothing is discarded,
  including captures in which nothing qualifies.

Credit budget: cost is (markets × regions) per call = 2 credits. Five
captures per matchweek ≈ 10 credits; eight matchweeks ≈ 80. The free
tier's 500/month is ample, and the experiment must not be redesigned to
consume more.

## 4. Benchmarks — two of them, reported side by side

**Ladbrokes is excluded from every benchmark it is measured against.**

**Benchmark A — sportsbook consensus.** For each competing sportsbook:
implied probabilities across the market, overround, then proportional
margin removal (`fair = implied / (1 + overround)`), per
`scripts/edge_calculator.py`. Consensus = **median** across books.
Median, not mean, to limit the pull of one stale quote.

**Benchmark B — exchange.** Betfair Exchange and/or Matchbook where
returned, treated separately and never blended into A. Their margin sits
in commission on net winnings, not in the quoted price, so proportional
margin removal does not mean the same thing for them. (Ruling carried
from Experiment 01; see `HALTED.md`.)

**Sensitivity checks on Benchmark A**, both computed every time:
Shin's method for margin removal, and consensus from only the two
lowest-overround books.

## 5. Selection rule — fixed now

A selection **qualifies** when:

```
(ladbrokes_price / benchmark_A_fair_price) - 1  >=  0.03
```

under the primary proportional method **and** both sensitivity checks.
If the three disagree, it is recorded as **not qualifying**, flagged
`method_sensitive: true`. Disagreement among reasonable methods is
evidence of noise.

Benchmark B is recorded and reported for every selection but **does not
gate qualification** in this experiment. Making it a gate would be a
different hypothesis; it is registered here as an observation only, so
that a future experiment can be designed on it honestly rather than
discovered in this one's data.

Everything screened is recorded — qualifying and not. Non-qualifying
observations are the control group and the expected majority.

## 6. A structural expectation, recorded in advance

Round 01 surfaced something that should be stated before more data
arrives, so a low qualifying rate is not later mistaken for a bug:

The rule compares a **margined** Ladbrokes price against a
**margin-removed** consensus. Clearing +3% therefore requires Ladbrokes
to price one outcome roughly 9 percentage points better than its own
book average — effectively running a negative margin on that leg. That
is the correct test for genuine positive expected value, and it is
deliberately not relaxed. But it means **qualifying selections should be
expected to be rare**, and their rarity is a finding about the market,
not a defect in the instrument.

## 7. Survival test

For each qualifying selection, the next scheduled capture determines
whether it still qualifies. Recorded: survival at the next capture, and
at the final pre-kickoff capture. A selection that has vanished by the
next capture is a data point about market speed and counts as an
**executability failure**, not a detection success.

## 8. Secondary objective — measure CLV properly, for the first time

Codex's review of `model-v1-backtest.md` established that what this
project has been calling CLV is not CLV: it compared *model
probabilities* against *closing probabilities*, which is model-vs-market
disagreement.

Real closing line value requires a price **available at decision time**
and the **actual closing price**. The capture schedule in section 3
produces both. So, independently of the qualifying rule, this experiment
records for every screened outcome: the Ladbrokes price at each capture,
and the final pre-kickoff price. This yields the project's first true
CLV series, and it accrues whether or not anything ever qualifies.

This is an observation, not a hypothesis under test here.

## 9. Duration and stopping rule

- **Eight matchweeks**, or 800 screened outcomes, whichever comes first.
- No early stop because results look good. No extension because they
  look bad.
- A discovered measurement fault halts the experiment and triggers
  re-registration as Experiment 03.

## 10. Decision rule — written before any data

A subsequent real-money trial is justified **only if all four hold**:

1. Qualifying selections occur at a rate of **at least 1 in 40**
   screened outcomes.
2. **At least 50%** of qualifying selections still qualify at the next
   scheduled capture.
3. Median measured edge among qualifying selections is **≥3%** under all
   three Benchmark A methods.
4. Qualifying selections are **not concentrated in a single bookmaker's
   quotes** dragging the median, and not concentrated in a single
   fixture, matchweek, or market.

**If any one fails, the answer is no, and this project stops looking for
edge in retail football betting.** Both analysts currently expect that
outcome.

**Explicitly not a success criterion:** whether qualifying selections
would have won. Outcomes at this sample size are noise and must not be
used to validate the method — in either direction.

## 11. What this cannot establish

- Not proof of a true probability edge. A price above consensus fair
  means the consensus disagrees with Ladbrokes, not that Ladbrokes is
  wrong.
- Nothing about how long an account stays unrestricted while taking such
  prices.
- API prices may lag each bookmaker's live price. That bias points
  toward *finding* false opportunities, so positives deserve more
  scepticism, not less.
- Nothing about whether this is worth doing at £10 stakes. Codex's
  arithmetic stands: a genuine 3% ROI is ~30p a bet. This answers *"does
  an edge exist?"*, not *"is it worth having?"*

## 12. Money

**None.** No stake is placed on anything arising from this experiment
while it runs. The separate question of whether to continue staking the
existing selection rule is untouched by this document — both analysts
have recommended stopping, and that remains the owner's decision.
