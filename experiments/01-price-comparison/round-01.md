# Experiment 01 — Round 01 (baseline)

**Observation round run 19 September 2026, ~19:15–19:45 BST**, against
Matchweek 5 fixtures kicking off 20 September. Screen run under the
pre-registration at `spec/experiment-01-price-comparison.md`, committed
before any data was collected. No threshold, method or rule was changed.

**Result: 0 qualifying selections from 12 screened outcomes across 4
markets.** That is the expected outcome (H0) and it is not a
disappointment.

---

## 1. What was screened

| Fixture | Market | Books in consensus | Not read |
|---|---|---|---|
| Bournemouth v Liverpool | match result | 21 | Ivy Bet (blank) |
| Leeds v Crystal Palace | match result | 21 | Ivy Bet (blank) |
| Man City v Sunderland | match result | 22 | — |
| Fulham v Man Utd | match result | 22 | — |

Observations are committed at
`experiments/01-price-comparison/observations/`, with the raw
as-displayed fractional captures under `observations/raw/` so every
decimal in the screen can be traced back to a fraction read off a
specific screenshot.

**Not screened, and why:**

- **Nottingham Forest v Coventry — excluded, already in play.** The
  directive listed it as un-kicked-off, but by the time the round ran it
  had started (17:30 kickoff, captured at 19:20). The first capture
  showed a sparse grid with Ladbrokes empty; five seconds later the grid
  repopulated with wholly different prices (bet365 Forest 8/13 → 1/5,
  Coventry 4/1 → 66/1). In-play prices are not the pre-match market and
  were not recorded as such.
- **All BTTS markets — not captured.** See section 4. This is a capture
  failure, not a decision, and it halves the intended round.

## 2. Results

Edge = `(Ladbrokes price / consensus fair price) - 1`, per section 5.

| Fixture | Outcome | Ladbrokes | Fair | Proportional | Shin | Two-lowest | Qualifies |
|---|---|---|---|---|---|---|---|
| BOU-LIV | Bournemouth | 3.10 | 3.258 | −4.84% | −5.15% | −4.74% | No |
| BOU-LIV | Draw | 3.75 | 3.955 | −5.19% | −6.45% | −5.14% | No |
| BOU-LIV | Liverpool | 2.10 | 2.283 | −8.02% | −6.61% | −7.65% | No |
| LEE-CRY | Leeds | 1.73 | 1.794 | −3.71% | −2.04% | −3.75% | No |
| LEE-CRY | Draw | 3.90 | 4.080 | −4.41% | −6.31% | −4.33% | No |
| LEE-CRY | Crystal Palace | 4.40 | 4.982 | −11.68% | −13.78% | −13.11% | No |
| MCI-SUN | Man City | 1.33 | 1.389 | −3.97% | −1.40% | −3.34% | No |
| MCI-SUN | Draw | 5.75 | 5.795 | −0.78% | −4.08% | −0.74% | No |
| MCI-SUN | Sunderland | 8.00 | 9.357 | −14.51% | −21.78% | −18.06% | No |
| FUL-MUN | Fulham | 3.30 | 3.595 | −8.19% | −8.86% | −9.54% | No |
| FUL-MUN | Draw | 3.70 | 3.938 | −6.04% | −7.42% | −5.88% | No |
| FUL-MUN | Man Utd | 2.05 | 2.133 | −3.87% | −2.44% | −3.34% | No |

- Markets screened: **4**. Outcomes screened: **12**.
- Qualifying: **0**. Qualifying rate: **0.0000**.
- Method-sensitive: **0** — no outcome came close enough to the
  threshold for the three methods to disagree about it.
- Median edge: **−5.02%**. Best: **−0.78%**. Worst: **−14.51%**.
- **Not one of the 12 edges was positive.**
- Survival re-check at +15 / +60 min (section 6): **not required**, since
  it applies only to qualifying selections and there were none.

## 3. Why nothing qualified — and a structural point about the threshold

This is worth stating precisely, because it will recur every round.

Ladbrokes' own booksum was 1.0654, 1.0626, 1.0489 and 1.0611 across the
four markets — a 4.9–6.5% margin, right in line with the market median
(6.1–6.7%). If Ladbrokes simply spread that margin evenly across all
three outcomes, **every** edge would land between −4.7% and −6.1%. The
observed median of −5.02% is almost exactly that.

So Ladbrokes is, this week, pricing like an ordinary margined book
sitting on the consensus. It is not systematically generous and not
systematically mean; it is mid-pack.

The structural consequence, stated now rather than after it becomes
inconvenient: the rule compares a **margined** Ladbrokes price against a
**margin-removed** fair price. To clear +3%, Ladbrokes must price a
single outcome roughly **9 percentage points better than its own average
pricing** — effectively running a negative margin on that leg. That is
the correct test (it is exactly the test of whether a price is genuinely
+EV), but it means qualifying selections should be expected to be rare,
and to come from specific errors or boosts rather than from ordinary
price variation.

**No threshold has been changed and none should be.** This is recorded
as a prediction about where the experiment is heading, and as the reason
a low qualifying rate should not later be mistaken for a bug.

Two secondary observations:

- **Longshots are shaded hardest.** The three worst edges are Sunderland
  at 8.00 (−14.5%), Crystal Palace at 4.40 (−11.7%) and Fulham at 3.30
  (−8.2%). The favourite-longshot bias is plainly visible. If a
  qualifying selection ever appears, it is far more likely to be a
  favourite than a longshot.
- **Method disagreement is largest exactly where the edge is most
  negative.** On Sunderland the three methods span 7.3 percentage points
  (−14.5% / −21.8% / −18.1%). In a lopsided market the choice of
  margin-removal method matters enormously. The method-sensitivity flag
  is therefore doing real work, and any future near-threshold longshot
  should be treated with suspicion.

## 4. Capture problems encountered

Recorded in full, because these determine whether the experiment is
runnable at all.

1. **Bookmaker names are images, prices are text.** `get_page_text`
   returns exact odds (no OCR risk) but **no bookmaker names** — the
   logos are images. Identifying which column is Ladbrokes therefore
   requires a screenshot every single time.

2. **The column count varies between pages.** Bournemouth–Liverpool and
   Leeds–Palace returned 24 values per row; Man City–Sunderland and
   Fulham–Man Utd returned 25. The cause: Ivy Bet had no price on the
   first two, and **blank cells are silently omitted from the DOM text**.
   A blank column before position 6 would shift the Ladbrokes column and
   produce a wrong price with no error and no obvious tell. On both
   24-column pages the blank was verified on screenshot to sit at
   position 20, after Ladbrokes. **This is the single most dangerous
   failure mode in the method** and it was found only because the counts
   happened to differ between fixtures.

3. **Row order differs on every page.** Liverpool/Bournemouth/Draw;
   Leeds/Draw/Palace; Man City/Draw/Sunderland; Man Utd/Fulham/Draw.
   Home-first is not reliable, draw-in-the-middle is not reliable.
   Labels must be read from the page every time.

4. **OCR on the grid is genuinely unreliable.** An early zoomed
   transcription of the Bournemouth–Liverpool row disagreed with the DOM
   at column 13 (read as 11/10, actually 23/20). Values are now taken
   from DOM text and only the *column identity* from the screenshot —
   but that split is the reason the round is trustworthy, and it was
   arrived at by catching an error, not by design.

5. **BTTS has no stable URL.** `/both-teams-to-score` returns 404 on
   these fixtures. BTTS is reachable only through an in-page market
   accordion, and its grid did not come back through `get_page_text` at
   all — it required a screenshot, i.e. the OCR path that problem 4 shows
   is unreliable. **All four BTTS markets were dropped rather than
   guessed**, per the directive's instruction to record omissions rather
   than estimate values.

6. **Prices move inside the capture window.** One book's Bournemouth
   price changed between two captures roughly a minute apart. Nothing in
   this round depends on it, but it is a direct preview of what the
   +15/+60 minute survival test will be measuring.

7. **Three bookmaker names are uncertain** — rendered here as
   "ForTheBettor", "BetAhoy" and "BetTOM" from small logos. They are
   labels only and enter no calculation, but they are flagged rather than
   presented as known.

## 5. An unresolved gap in the pre-registration — for the owner

Section 4 says to capture "every bookmaker's price". oddschecker lists
**Betfair Exchange and Matchbook under a separate "Exchanges" heading**.
Exchanges are not bookmakers and carry near-zero margin, so including
them would materially tighten the consensus and, in particular, would
dominate the two-lowest-margin sensitivity check.

**This round was run with sportsbooks only.** The exchange prices are
preserved in every observation file under `exchange_prices`, so the
other reading can be computed later without recapturing anything. It
would not have changed this round's result — including exchanges makes
qualifying strictly harder, and nothing qualified.

I have not resolved this, because resolving it would be reinterpreting
the specification. **It needs an owner ruling before round 2.**

A related concentration risk, relevant to decision rule item 4: **AK Bets
had the lowest overround in all four markets** (1.86%, 2.39%, 2.58%,
2.87%). The "two lowest-margin books" check is therefore in practice
"AK Bets plus one other" nearly every week. If a qualifying selection
ever passes that check, it will need to be examined for exactly the
single-quote artefact the decision rule warns about.

## 6. Time spent, honestly

Roughly **45 browser interactions over about 75 minutes** produced
**4 markets**. Most of that was not reading prices — it was verifying
that the Ladbrokes column was really the Ladbrokes column, and
re-capturing pages whose grids I could not prove were aligned.

Extrapolating at the observed rate:

| | |
|---|---|
| A full matchweek (10 fixtures × 2 markets) | ~20 markets |
| Time at the observed rate | **~6 hours per week** |
| Eight matchweeks | **~48 hours**, for ~160 screened markets |

Note that at ~20 markets per week, the section 8 stopping rule binds on
**eight matchweeks, not 500 markets** — the experiment will end with
roughly 160 markets, not 500.

## 7. Is this sustainable weekly for eight weeks? — the honest answer

**No, not in this form.** Three reasons, in order of seriousness.

**1. The method is not merely slow, it is silently fragile.** Six hours a
week is survivable if tedious. The real problem is failure mode 2: a
blank cell before column 6 shifts every reading with no error raised, and
the only defence is a human (or model) eyeballing a logo strip on every
page, every week. This round found that problem by luck — two fixtures
happened to have different column counts. A week where *all* pages have
24 columns would produce a confidently wrong dataset. An experiment
designed to make "no opportunities found" the default becomes worthless
if its most likely bug manufactures fake opportunities.

**2. Half the intended universe was not capturable at all.** BTTS is 50%
of the pre-registered market scope and 0% of what was collected. Section
3 of the pre-registration specifically notes the BTTS pause does not
apply here. If BTTS cannot be captured reliably, the experiment is
testing half of what it was registered to test.

**3. The dataset will be too small for the decision rule to discriminate.**
At ~160 markets over eight weeks, decision rule item 1 (a qualifying rate
of at least 1 in 40) implies about four qualifying selections at the
boundary. Distinguishing "1 in 40" from "1 in 80" on that sample is not
realistically possible, and items 2 and 3 — survival rate and median edge
*among qualifying selections* — would be computed on a handful of
observations.

### What I recommend, and what I have deliberately not done

I have **not** changed any threshold, rule or method, and have not
improvised a variant. The pre-registration is intact and this round was
run under it exactly as written.

The directive asked me to say now if the method is too slow or unreliable
to sustain for eight weeks, because that would be a reason to redesign
before collecting more data. **It is.** My recommendation is to halt
after this baseline round and re-register as Experiment 02 with a
different capture mechanism — an odds API or feed that returns
`{bookmaker: price}` pairs directly, eliminating the column-alignment
problem entirely, making BTTS capturable, and making a much larger
sample cheap enough that the decision rule can actually discriminate.
Section 8 already prescribes exactly this route: halt, document the
fault, re-register — do not silently reuse data collected under a
known-fragile method.

That is a recommendation to the owner, not a decision taken here. The
tooling is built and tested, the pre-registered rule works end to end,
and this round's 12 observations stand on their own — every Ladbrokes
column in them was verified against a screenshot before use.

## 8. Reproducing this round

```
python3 scripts/build_observation.py \
    experiments/01-price-comparison/observations/raw/*.json \
    --out-dir experiments/01-price-comparison/observations

python3 scripts/price_screen.py \
    experiments/01-price-comparison/observations/*.json
```

`build_observation.py` refuses to build a market whose transcribed row
length does not match its column count — the guard against failure mode 2.

**No money was staked, no ledger was touched, no pick was generated, and
the BTTS pause is untouched.**
