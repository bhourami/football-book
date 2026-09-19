# Experiment 01 — Is Ladbrokes sometimes mispriced against the market?

**Pre-registration. Written and committed 19 September 2026, BEFORE any
data was collected.** Nothing in this document may be changed once data
collection begins. If something here turns out to be badly designed,
the experiment is abandoned and re-registered as Experiment 02 with the
reason recorded — it is never quietly edited mid-flight.

This exists because everything this project has done so far failed in
the same direction: it enthusiastically found edge that wasn't there
(72.5% of markets selected; a systematic one-directional BTTS skew; two
confirmed reasoning errors). A pre-registered rule with a fixed
threshold is the mechanism that makes **"no opportunities found"** the
expected, unremarkable output.

---

## 1. The question

Not *"can we forecast football better than the market?"* — that was
answered no, empirically, over 1,180 matches
(`collaboration/debates/model-v1-backtest.md`).

Instead: **does Ladbrokes, the bookmaker the owner actually bets with,
sometimes offer a price materially better than the wider market's
margin-adjusted consensus — and does that price survive long enough for
a human to place it manually?**

This requires no forecasting model, no xG, no team-news judgement, and
no opinion about who will win. It is a price-comparison question.

## 2. Hypothesis, stated before data

**H1:** Ladbrokes' price exceeds the market consensus fair price by
≥3% on some non-trivial fraction of Premier League match-result and
BTTS selections.

**H0 (the expected result):** it does not, or such instances are so
rare, so short-lived, or so concentrated in unbettable circumstances
that they cannot be acted on manually.

**We expect H0.** Most observation rounds should produce zero
qualifying opportunities. A round producing many qualifying
opportunities is more likely to indicate a measurement fault — stale
displayed prices, a mis-parsed column, a market that has already moved
— than a genuine finding, and must be investigated as such before
being recorded as a result.

## 3. Universe

- Competition: Premier League only.
- Markets: match result (1X2) and both-teams-to-score.
- Fixtures: every fixture in the current matchweek, no exclusions,
  no discretionary selection of "interesting" matches.
- Note: the BTTS pause in `methodology.md` section 7 bars BTTS
  selections derived from **our model**. It does not apply here,
  because this experiment forms no probability estimate of its own.

## 4. Benchmark: how "fair price" is computed

For each market, from `oddschecker.com`:

1. Capture every bookmaker's price for every outcome, with a timestamp.
2. **Exclude Ladbrokes' own price from the consensus.** Ladbrokes is
   the subject of the measurement and must not contribute to the
   benchmark it is measured against.
3. For each remaining bookmaker, compute implied probabilities across
   all outcomes in that market and the resulting overround.
4. Primary benchmark — **proportional margin removal**, per
   `scripts/edge_calculator.py`: `fair = implied / (1 + overround)`,
   applied per bookmaker, then take the **median** fair probability
   across bookmakers for each outcome. Median, not mean, to limit the
   influence of one stale or erroneous quote.
5. Fair price = `1 / median fair probability`.

**Sensitivity check, computed and reported alongside, never instead
of:** the same calculation using Shin's method for margin removal, and
the same calculation using only the two lowest-margin books available.
If the three methods disagree about whether an opportunity qualifies,
it is recorded as **not qualifying** and flagged as
method-sensitive. Disagreement between reasonable methods is evidence
of noise, not of opportunity.

## 5. Selection rule — fixed now

A selection **qualifies** when:

```
(Ladbrokes price / consensus fair price) - 1  >=  0.03
```

i.e. Ladbrokes offers at least 3% more than the market's fair price,
under the primary benchmark **and** both sensitivity checks.

Everything observed is recorded — qualifying and non-qualifying alike.
Non-qualifying observations are the control group and are the majority
of the expected dataset. They are never pruned.

## 6. Survival test — does the price last long enough to bet?

For every qualifying selection, re-capture the Ladbrokes price and the
consensus at **+15 minutes** and **+60 minutes**.

Record for each: whether the selection still qualifies, the price now,
and the consensus now. A price that has vanished by +15 minutes is not
an opportunity for a human placing bets by hand — it is a data point
about market speed, and counts as a failure of executability, not a
success of detection.

## 7. What is measured

Per observation round, and cumulatively:

- Number of markets screened.
- Number and rate of qualifying selections (expected: low or zero).
- Median and distribution of the measured percentage edge.
- Survival rate at +15 and +60 minutes.
- Method-sensitivity: how many qualified under the primary benchmark
  but failed a sensitivity check.
- Wall-clock time spent per observation round, honestly recorded.
- Where a qualifying selection's fixture later settles, the outcome —
  though see the warning in section 9 about what outcomes can and
  cannot tell us at this sample size.

## 8. Duration and stopping rule

- **Eight matchweeks**, or 500 screened markets, whichever comes first.
- No early stopping because results look good. No extension because
  results look bad.
- If a measurement fault is discovered mid-experiment, the experiment
  halts, the fault is documented, and it is re-registered as
  Experiment 02. Data collected under a known-faulty method is not
  silently reused.

## 9. Decision rule — written before seeing any result

Stated now so it cannot be rationalised later.

**This experiment justifies a subsequent real-money trial only if
all four hold:**

1. Qualifying selections occur at a rate of **at least 1 in 40**
   screened markets (rarer than that and there is nothing to operate).
2. **At least 50%** of qualifying selections still qualify at +15
   minutes (they must be humanly placeable).
3. The median measured edge among qualifying selections is
   **≥3%** under all three margin-removal methods.
4. Qualifying selections are **not concentrated in a single
   bookmaker-quote artefact** — e.g. all arising because one book's
   stale price dragged the median.

**If any one fails, the answer is no, and this project stops looking
for edge in retail football betting.** That is a legitimate and
valuable outcome, and it is the outcome both analysts currently expect.

**Explicitly not a success criterion:** whether qualifying selections
would have won. At the sample sizes available here, outcomes are noise.
A run of winners does not validate this and must not be used to.

## 10. What this experiment cannot establish

Stated plainly so it is not over-claimed later:

- It cannot prove a *true* probability edge. A price better than
  consensus fair is evidence the consensus disagrees with Ladbrokes,
  not proof that Ladbrokes is wrong.
- It cannot establish how long an account stays unrestricted while
  taking such prices. That risk sits outside this measurement entirely.
- oddschecker's displayed prices may lag each bookmaker's live price.
  Every measurement inherits that lag. This biases toward *finding*
  false opportunities, which is the direction that should make us more
  sceptical of positives, not less.
- Even a clean positive result says nothing about whether this is worth
  doing at £10 stakes. Codex's arithmetic stands: a genuine 3% ROI is
  ~30p a bet. This experiment answers *"does an edge exist?"*, not
  *"is it worth having?"*

## 11. Money

**None.** No stake is placed on anything arising from this experiment
while it runs. The existing separate question of whether to keep
staking the current selection rule is unaffected by this document —
both analysts have recommended stopping that, and it remains the
owner's decision.
