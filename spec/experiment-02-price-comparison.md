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

---

## Amendment, 20 September 2026 — made BEFORE any data was collected

An API key arrived and the instrument was tested before the first
capture. The test spent 2 credits and produced **zero observations**;
nothing was screened, no edge was computed, and none of that pre-flight
data will be used as experiment data.

This is recorded as an amendment rather than a re-registration as
Experiment 03 because **collection never began**. The question, the 3%
threshold (section 5), the decision rule (section 10) and the stopping
rule (section 9) are all unchanged. What changed is one arithmetic
error and one exclusion list that was not strict enough. Both changes
make the measurement harder to pass, not easier, and both were made
blind to any computed edge.

### Finding 1 — BTTS is not on the bulk endpoint, and the credit budget in section 3 is wrong

`GET /v4/sports/soccer_epl/odds?markets=h2h,btts` returns **HTTP 422
INVALID_MARKET**. BTTS is an additional market, available only from the
per-event endpoint, one credit per fixture.

Section 3 said a capture costs 2 credits, five captures a matchweek
≈ 10, and eight matchweeks ≈ 80. The true cost:

| | credits |
|---|---|
| Match result, all fixtures in one call | 1 |
| BTTS, per fixture × 10 | 10 |
| **One capture** | **11** |
| One matchweek (5 captures) | 55 |
| **Eight matchweeks** | **440** |

**That is 5.5× the registered estimate.** It still fits the free tier,
which is 500 credits *per month* and resets: eight matchweeks span about
three months, so the peak month is roughly 165 credits. But the figure
in section 3 was wrong and is corrected here rather than quietly
absorbed.

`collect_odds.py` takes `--horizon-hours` (default 30) so a capture
spends BTTS credits only on the matchweek in hand, never on every
fixture the API happens to list three weeks out.

### Finding 2 — Coral is Ladbrokes, and was inside the benchmark

Section 4 excludes Ladbrokes from every benchmark it is measured
against. It did not exclude **Coral**, which is the same operator
(Entain). On Fulham v Man Utd, 20 September 2026:

| | Home / Draw / Away | BTTS Yes / No |
|---|---|---|
| Ladbrokes | 3.40 / 3.70 / 2.00 | 1.50 / 2.45 |
| Coral | 3.40 / 3.70 / 2.05 | 1.50 / 2.45 |

Identical on BTTS, one tick apart on the match result. Leaving Coral in
the consensus measures Ladbrokes partly against itself — exactly the
error section 4 excludes Ladbrokes to avoid, and it biases toward
*finding* opportunities, the direction this experiment must be most
sceptical of.

**Coral is excluded from Benchmark A from the outset.** Its prices are
still captured and recorded, in `subject_affiliate_prices`.

### Finding 3 — two brands, one pricing desk

LiveScore Bet and Virgin Bet returned identical prices on both markets
(3.60 / 3.65 / 1.93 and 1.47 / 2.55). Counting both lets one desk pull
the median twice, which is the concentration section 10(4) says must
not drive a result.

**Brands under one operator contribute a single quote to the
consensus** — the per-outcome median of their members, with every member
preserved in `group_members`. This is decided on ownership, fixed in
advance, not on whether two prices happen to match on a given day.

### Finding 4 — the exchange ruling was right, and mattered more than expected

Betfair Exchange, Matchbook and Smarkets all returned about
3.70 / 3.95 / 2.05 — clearly better than every sportsbook, and nearly
identical to each other. Had they been blended into Benchmark A as
section 4 of Experiment 01 originally contemplated, three correlated
exchange quotes would have dragged the consensus and manufactured
apparent Ladbrokes value on almost every outcome. The ruling carried
over from `HALTED.md` prevented that. Recorded because it is the first
time a design decision in this project has been vindicated in advance
rather than corrected afterwards.

### Benchmark pool after these exclusions

Of 20 books quoting the match result: minus Ladbrokes (subject), minus
Coral (same operator), minus 3 exchanges (Benchmark B), minus one
duplicate brand = **14 independent quotes**. BTTS is quoted by 10 books,
leaving **5** after the same exclusions. Thin, and worth watching — a
5-book median is more fragile than a 14-book one, and if BTTS coverage
drops further that is itself a finding about whether this market is
measurable at all.
