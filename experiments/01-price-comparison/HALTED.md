# Experiment 01 — HALTED after one round

**Halted 19 September 2026**, under section 8 of its own pre-registration:
*"If a measurement fault is discovered mid-experiment, the experiment
halts, the fault is documented, and it is re-registered as Experiment 02.
Data collected under a known-faulty method is not silently reused."*

This is the pre-registration working as intended, not the experiment
failing. The halt is on the **method**, not the result.

## The fault

Prices were read from oddschecker's bookmaker grid via browser capture.
oddschecker drops blank cells from the DOM rather than rendering an empty
column. A single blank cell *before* the Ladbrokes column therefore shifts
every subsequent price by one position, **silently** — no error, no
malformed value, just a confidently wrong dataset attributing another
bookmaker's price to Ladbrokes.

It was caught only because two fixtures happened to render different
column counts (24 vs 25). Had every page in a given week rendered the same
count, the error would have been invisible and the data would have looked
clean.

**Why this is disqualifying rather than an inconvenience:** this
experiment was designed so that *finding nothing* is the default output.
Its most likely failure mode manufactures false opportunities. An
experiment whose principal bug points in the exact direction of its
hypothesis cannot be trusted to reject that hypothesis.

## Secondary problems, each sufficient on its own

- **BTTS was 0% captured** despite being half the registered scope
  (section 3). No stable market URL, grid only recoverable by OCR.
- **Statistical power.** Eight weeks at this capture rate yields ~160
  markets. The decision rule (section 9) requires distinguishing a
  qualifying rate of 1-in-40 from lower rates. 160 observations cannot
  separate 1-in-40 from 1-in-80.
- **Cost.** ~6 hours per week of manual capture, for a dataset that is
  half-missing and structurally fragile.

## What round 01 nevertheless established

The single completed round is retained (`round-01.md`, observations under
`observations/`) and is **not** used as evidence for or against H1, per
the rule above. But two things it showed are worth carrying forward:

1. **Ladbrokes is mid-pack, not generous.** 0 of 12 outcomes qualified;
   not one edge was positive; median −5.02%. Its margin (4.9–6.5%) sat
   inside the market median (6.1–6.7%).
2. **The favourite-longshot bias is plainly visible** — the three worst
   prices were the three longest (Sunderland 8.00 at −14.5%, Palace 4.40
   at −11.7%, Fulham 3.30 at −8.2%). This is a well-documented real
   effect, and its clean appearance is mild evidence the *arithmetic*
   was working even though the *capture* was fragile.

Neither is a finding. Both are hypotheses for Experiment 02 to test
properly.

## Unresolved question, carried into Experiment 02

Section 4 said "every bookmaker's price". oddschecker lists Betfair
Exchange and Matchbook, which are **exchanges**, not bookmakers. The
round-01 operator correctly declined to resolve this unilaterally and
preserved exchange prices in every observation so either reading remains
computable.

**Ruling, made now and carried into Experiment 02's design:** exchanges
are a **separate benchmark**, never blended into the sportsbook median.
Their margin structure is fundamentally different — commission charged on
net winnings rather than built into the quoted price — so proportional
margin removal does not mean the same thing when applied to them. Mixing
the two into one median is methodologically muddled. Experiment 02
reports both benchmarks side by side.

## Status

Superseded by `spec/experiment-02-price-comparison.md`. No money was
staked at any point under Experiment 01.
