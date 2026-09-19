# Model v1: fitted Dixon-Coles, backtested against the closing line

19 September 2026. Built in response to the systematic BTTS-No skew the
owner caught, and to his broader point: *"you guys ain't doing enough
research for the picks, you're gambling 50/50 right now."*

## The headline: the model does not beat the closing line

**It does not. Not at any edge threshold. This is the most important
result in this document and it is not a close call.**

| Edge threshold | Selections | Win % | ROI | Beat closing line | Mean CLV |
|---|---|---|---|---|---|
| 2% | 1,180 | 32.6% | -2.64% | 49.7% | +0.0005 |
| **3% (current rule)** | **970** | **32.3%** | **-6.14%** | **49.9%** | **+0.0006** |
| 5% | 671 | 31.7% | -11.88% | 49.0% | -0.0000 |
| 8% | 383 | 30.5% | -12.08% | 51.4% | +0.0001 |
| 10% | 259 | 32.4% | -6.75% | 52.9% | +0.0005 |
| 15% | 89 | 29.2% | +1.35% | 53.9% | +0.0025 |
| 20% | 28 | 14.3% | -25.71% | 50.0% | +0.0040 |

Beat-the-close sits at ~50% at every threshold — a coin flip — and mean
CLV is ~0.000 to 0.004 implied-probability points, i.e. indistinguishable
from zero. The lone positive ROI cell (15%, +1.35%) is 89 selections and
is immediately contradicted by the 20% row collapsing to -25.7%. That is
noise, and reading it as a finding would be exactly the overfitting this
exercise was meant to avoid. **Every threshold was computed and all are
reported here; none was selected as "the answer".**

Under the project's actual live rule (3pp, one candidate per market,
struck at the opening price), this model would have made 856 selections
across 1,180 matches, staked £8,560, and lost **£787.30 — an ROI of
-9.20%** with **zero CLV**.

A 72.5% selection rate is itself the tell. A model finding exploitable
edge in seven of every ten matches is not finding edge; it is disagreeing
with the market constantly and at random. This is the *same signature*
the qualitative method showed when it took positions on nearly every
fixture in Matchweek 5 — same disease, and now measured rather than
suspected.

## What the model does get right: calibration

It is not a broken model. Match-result calibration is genuinely good:

| Predicted bucket | n | Predicted | Actual | Gap |
|---|---|---|---|---|
| 0.0-0.1 | 111 | 0.071 | 0.081 | +0.010 |
| 0.1-0.2 | 552 | 0.160 | 0.165 | +0.005 |
| 0.2-0.3 | 1,312 | 0.247 | 0.260 | +0.013 |
| 0.3-0.4 | 537 | 0.347 | 0.350 | +0.003 |
| 0.4-0.5 | 398 | 0.445 | 0.399 | -0.046 |
| 0.5-0.6 | 289 | 0.547 | 0.550 | +0.003 |
| 0.6-0.7 | 211 | 0.648 | 0.635 | -0.013 |
| 0.7-0.8 | 89 | 0.751 | 0.708 | -0.043 |
| 0.8-1.0 | 41 | 0.847 | 0.878 | +0.031 |
| **Overall** | **3,540** | **0.333** | **0.333** | **+0.000** |

So the model describes football reasonably well. It just describes it no
better than a bookmaker who has already priced it — which is the entire
question, and the answer is no.

## The BTTS question: the bias is real and survives a proper model

This is the finding that matters most for the pause currently in force.

| Predicted BTTS-yes | n | Predicted | Actual | Gap |
|---|---|---|---|---|
| 0.3-0.4 | 48 | 0.378 | 0.562 | **+0.185** |
| 0.4-0.5 | 295 | 0.460 | 0.522 | +0.062 |
| 0.5-0.6 | 549 | 0.552 | 0.592 | +0.040 |
| 0.6-0.7 | 274 | 0.633 | 0.620 | -0.013 |
| 0.7-0.8 | 14 | 0.720 | 0.714 | -0.006 |
| **Overall** | **1,180** | **0.543** | **0.581** | **+0.039** |

Mean model P(BTTS yes) = **0.543**. Realised rate = **0.581**. The model
under-predicts BTTS-yes by **3.85 percentage points on average**, and by
**18.5 points** in the lowest bucket — precisely where a "BTTS No" pick
would be most tempting.

**So the skew was not merely an artefact of qualitative guessing.** A
properly fitted Dixon-Coles model, with no hand-waving anywhere in it,
reproduces the same directional bias. The owner's instinct — *"I can't
see goalless matches from one team in every match"* — identified
something structural, not sloppiness.

The likely mechanism is well known and inherent to this model family:
independent Poisson scoring assumes the two teams' goal counts are
independent, when in reality they are positively correlated (open games
produce goals at both ends; cagey ones suppress both). Ignoring that
correlation systematically understates P(both score). The Dixon-Coles
`tau` correction patches only the four lowest score cells (0-0, 1-0,
0-1, 1-1) and does not fix the broader dependence.

**The BTTS pause should stay in force.** Neither method — qualitative or
fitted — currently produces trustworthy BTTS probabilities, and now we
know why rather than merely that.

## Limits of this test, stated plainly

- football-data.co.uk carries **no BTTS market price**, so BTTS could be
  tested for calibration against reality but **not** for edge or CLV
  against a market. The match-result CLV result is the real edge test.
- Refitting runs every 10 matches, warm-started, not every single match —
  a pure-Python speed compromise (no numpy/scipy on this machine). It
  should not materially change conclusions this lopsided.
- Hyperparameters (time-decay ξ=0.0025/day, 10×10 score grid, iteration
  counts) were set to literature-standard defaults **before** seeing any
  result and were not tuned afterwards. No variant hunting was performed
  beyond the single threshold sweep reported in full above.
- Test set is 2023-24 onward (1,180 matches). Real xG exists only for
  2026-27 (40 matches) and was therefore **not** used in fitting — too
  small to fit on. An xG-based model remains untested.

## Recommendation before any of this touches real money

1. **Do not deploy this model to pick bets.** It is calibrated but has no
   edge. Using it would convert a qualitative coin-flip into a
   quantitative coin-flip with better paperwork.
2. **Keep the BTTS pause.** It is now justified by measurement, not
   suspicion, and the cause is understood.
3. **The honest strategic finding:** two seasons of effort at beating the
   closing Bet365 line with public data produced zero CLV. That is the
   normal result — closing lines in a liquid market are hard to beat, and
   this is the evidence, not a reason to try harder with the same tools.
   Any future attempt should start by asking what information the market
   *doesn't* already have, rather than re-deriving what it does.
4. If the project continues, the next honest step is not a better fit —
   it is to test whether *anything* available here (real xG, shot
   quality, the Claude/Codex debate itself) generates CLV, measured this
   same way, before a single further pound is staked on it.
