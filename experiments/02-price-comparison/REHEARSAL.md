# Pre-flight and rehearsal, 20 September 2026 — NOT experiment data

Recorded so it is never mistaken for a result. Nothing here is used to
test H1, and none of it counts toward the eight matchweeks in section 9.
Collection proper has not begun.

## What was spent

| | credits |
|---|---|
| `/events` listing | 0 |
| Bulk `h2h` (all fixtures) | 1 |
| Per-event `btts` (Fulham v Man Utd) | 1 |
| T-15m availability probe | 2 |
| **Total** | **4 of 500** |

## What it established

The four findings that amended the pre-registration are in
[`spec/experiment-02-price-comparison.md`](../../spec/experiment-02-price-comparison.md)
under "Amendment, 20 September 2026": BTTS needs the per-event endpoint
and costs 5.5× the registered budget; Coral is Ladbrokes and was inside
the benchmark; LiveScore Bet and Virgin Bet are one pricing desk; the
exchange ruling was right and mattered.

## The rehearsal run, for the record

Fulham v Manchester United, the one fixture still pre-match when the key
arrived. 14 independent books in the match-result consensus, 5 in BTTS,
after all exclusions.

| Outcome | Ladbrokes | Consensus fair | Proportional | Shin | Two lowest margin |
|---|---|---|---|---|---|
| Fulham | 3.40 | 3.64 | −6.6% | −7.7% | −9.1% |
| Draw | 3.70 | 4.00 | −7.4% | −8.5% | −6.9% |
| Man Utd | 2.00 | 2.11 | −5.3% | −4.2% | −3.8% |
| BTTS Yes | 1.50 | 1.58 | −4.9% | −3.4% | −5.6% |
| BTTS No | 2.45 | 2.73 | −10.4% | −12.8% | −9.3% |

**Nothing qualified. Not one edge was positive**, under any of the three
margin-removal methods. Median −6.6%.

This is what the instrument working looks like. It is also consistent
with Experiment 01's single completed round (0 of 12 qualified, median
−5.02%) and with the structural expectation recorded in section 6: the
rule compares a margined Ladbrokes price against a margin-removed
consensus, so clearing +3% requires Ladbrokes to run a negative margin
on that leg.

**One fixture is not evidence of anything** and is not treated as any.
It is one afternoon's prices on one match, recorded because the
pre-registration says nothing is discarded — not because five negative
numbers tell us what eight matchweeks will.

## The T-15m slot works — checked, not assumed

Section 3 schedules a capture 15 minutes before kickoff. If the feed
switched to in-play or dropped the fixture near kickoff, that slot would
be unworkable, so it was probed on Fulham v Man Utd rather than assumed.

At exactly T-15m the fixture was **still listed with full pre-match
coverage** — 20 books on match result, 10 on BTTS, identical to 90
minutes earlier. The capture schedule is viable as registered.

The probe also gave the first look at whether there is any movement for
the survival test (section 7) and the CLV series (section 8) to measure.
There is:

| Outcome | T-90m | T-15m | Move | Edge T-90m | Edge T-15m |
|---|---|---|---|---|---|
| Fulham | 3.40 | 3.40 | — | −6.6% | −8.5% |
| Draw | 3.70 | 3.60 | −0.10 | −7.4% | −8.9% |
| Man Utd | 2.00 | 2.05 | +0.05 | −5.3% | −1.6% |
| BTTS Yes | 1.50 | 1.53 | +0.03 | −4.9% | −6.1% |
| BTTS No | 2.45 | 2.37 | −0.08 | −10.4% | −8.4% |

Four of five prices moved in 75 minutes, and the measured edge moved by
up to 3.7 percentage points. So a qualifying selection surviving to the
next capture is a genuine question rather than a formality — which is
exactly what section 7 was written to test. Book coverage held steady at
14 and 5 across both captures. Nothing qualified at either.

## When collection actually starts

**Matchweek 6, 10–12 October 2026.** Matchweek 5 was all but over when
the key arrived — three fixtures already in play and one an hour from
kickoff. Starting an eight-matchweek experiment on a single fixture
would produce a ragged first week for no gain, and section 3's capture
schedule (T-24h through closing) cannot be honoured retrospectively.
