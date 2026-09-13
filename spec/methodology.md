# Football Book — Frozen Methodology
Version: V1
Frozen: 12 September 2026
Last amended: 13 September 2026 (section 7 edge threshold set)
Status: authoritative. No session may change or reinterpret any
definition below. Conflicts are raised as errors, never resolved
locally. Source: `football-book-handoff.md`, written 12 September 2026
from the earnings desk.

Sections marked **OPEN** are not yet frozen. They require an explicit
owner decision before the first bet is placed. Do not fill them in
with a "reasonable default" — that is exactly the failure mode this
document exists to prevent.

## 1. Scope
Premier League only. Singles on match result (1X2) and both-teams-to-
score (BTTS). No accumulators in the live book (see section 12).
Expand to a second league only once a hundred settled bets exist in
the conclusion book.

## 2. Bank, stake and stop
Real money. £200 bank. Decided 12 September 2026, owner's call.
Flat £10 per bet, from bet one. No sizing by conviction until there
is evidence sizing adds anything (carried over from the earnings
desk's flat-stake-by-accident lesson — do it deliberately here
instead).

£200 / £10 = 20 bets maximum. That is the hard ceiling regardless of
bank balance at the time.

Stop rule, copied from the earnings desk's live-money precedent
(that document's section 19), written by the owner for himself:
- Hard cap per bet: £10.
- Hard maximum: 20 completed bets.
- Review checkpoint: after bet 10, before continuing to bet 11.
- **Terminates early** if any selection or stake is altered because
  of the live account's running profit or loss.
- **Stops automatically** at 20 bets or at bank exhaustion (£0),
  whichever comes first. Requires review before any further bet.
- **Never rolled forward because it is winning.**

The moment a selection or a stake changes because of what the account
is showing, the experiment has stopped measuring what it was built to
measure and should end there.

## 3. What is being measured
Twenty to forty bets cannot separate skill from luck on profit and
loss — it is not close. Closing line value (CLV, section 10) is the
**primary metric** from the first bet. Profit and loss is a
diagnostic, not the verdict. If the bank finishes up or down, that
alone proves nothing at this sample size; do not let it be treated as
proof in either direction.

## 4. Three books — decided
Claude alone, Codex alone, and the debated conclusion, each scored on
identical selections at identical prices, exactly as the earnings desk
ran it. **Decided 12 September 2026, owner's call: all three books are
real money.** Each carries its own real £200 bank at £10 flat stakes
(section 2), for £600 total real exposure across the three books, not
£200. Each book's stop rule (section 2) applies independently — one
book stopping at 20 bets or bank exhaustion does not stop the other
two, and a decision is never altered in one book because of another
book's running profit or loss.

## 5. Blind-before-debate protocol
Each analyst's selection is sealed before it sees the other's. This is
the single most expensive lesson carried over: in an earlier attempt,
Claude opened against an empty transcript while Codex's first turn
already contained Claude's, so the "Codex solo" book was really Codex
reacting to Claude, and the comparison was flattered without anyone
noticing until much later. That failure is invisible after the fact —
it can only be prevented mechanically, not caught by review.

Mechanical rule: both opening selections, with exact stakes and
prices, are written to `/collaboration/claude-input.json` and
`/collaboration/codex-input.json` respectively and **committed to
disk before either process is given the other's file, or any part of
its content, in context.** Claude writes only `claude-input.json`;
Codex writes only `codex-input.json`. Neither may be edited by the
other agent. See `/collaboration/PROTOCOL.md` for the full sequence,
including the debate stage that follows.

## 6. Fail-closed
A missing input is never a zero-becomes-a-bet. No team news, no bet.
If no honest independent probability estimate can be formed for a
fixture, that is a no-bet, recorded as `insufficient_evidence` in the
selection card (section 8) and logged in the rejected-selection audit
(section 9) exactly like any other decline.

**Decided 13 September 2026, owner's call: "team news confirmed" means
the official starting lineup (teamsheet) has been published** —
typically around an hour before kick-off — not the pre-match
injury/doubt reporting used to form the initial probability estimate.
A selection formed from pre-lineup reporting is **provisional**: it
must be re-checked against the actual confirmed lineup before the
bet is placed. If the real lineup differs materially from what the
estimate assumed (an expected absentee starts, a expected starter is
rested, an unreported change), the probability estimate and edge are
recomputed at that point, and the selection can flip from taken to
declined or vice versa. A provisional selection is not itself a
completed selection card — it becomes one only once the lineup check
has happened, recorded with its own timestamp.

## 7. Edge and the selection rule — decided
Every price states a strike rate. There is no bet unless our own
probability estimate differs from the market's fair probability, and
differs by more than a stated threshold. A team can look excellent and
still not be a bet, because the price already says it is excellent.

**Decided 13 September 2026, owner's call: minimum edge = 3 percentage
points.** A selection qualifies only when our probability estimate
exceeds the fair probability (section 7 formula below) by at least
0.03. Below that, the selection is declined and logged in the
rejected-selection audit (section 9) like any other decline, with
`decision_reason: edge_below_threshold`.

This is a starting floor, not a permanent one. It may be revisited
after a first batch of results — but only as a deliberate, dated,
written change to this section, never adjusted mid-run to fit how a
bet or a run of bets turned out (frozen rules, top of this document).

    implied probability   = 1 / decimal odds
    overround             = sum of implied probabilities
                             across the market, minus 1
    fair probability      = implied / (1 + overround)   [proportional method]
    edge                  = our probability - fair probability
    break-even strike     = fair probability

Reference implementation: `/scripts/edge_calculator.py`.

Our probability must come from a stated model — base rates, xG-
derived expectations, home advantage, availability — fitted before the
fixture and never adjusted after seeing the price. Anchoring an
estimate to the odds and then declaring an edge is the easiest self-
deception available here; it produces a book that always agrees with
itself and must not happen.

## 8. Selection card
Every selection — taken or rejected — records these fields before
kick-off:

- fixture (teams, competition, kick-off time, UTC)
- market (match result | BTTS)
- our probability estimate, and the method/source it came from
- price obtained, source, and timestamp (odds move; the price recalled
  afterwards is not evidence)
- overround for that market at that price
- fair probability and required (break-even) strike rate
- edge (our probability minus fair probability)
- stake (£10, or £0 if declined)
- decision: taken | declined, and reason if declined
- team news status: confirmed | unconfirmed (unconfirmed forces
  fail-closed, section 6)
- result and settlement (added after full time)
- closing price and CLV (added at kick-off, section 10)

Template: `/ledger/selection-card.schema.json`.

## 9. Rejected-selection audit
Every declined selection carries the identical selection-card fields
as a taken one, logged to `/requests/rejected-selections.json`. This
audit is what makes the reason a book leads or lags visible — on the
earnings desk, the leading book led entirely on two refusals that
would have been invisible without this record. Score rejections on
the same dates as taken bets, on the same schedule.

## 10. Closing line value (CLV)
Recorded on every bet from the first one, and treated as primary
(section 3). CLV = whether the price obtained beat the closing price,
expressed as the difference in implied probability (or fair
probability, consistently) between the two. Beating the close
consistently is evidence of edge even while losing money on paper and
loss; losing to the close while winning money is evidence of luck, not
skill. CLV carries signal at twenty to thirty bets, where profit and
loss needs hundreds.

## 11. Calibration
Bucket every claimed probability and compare it against realised
frequency (of selections given roughly 60%, did about 60% land?). This
is tracked from the first bet, alongside CLV, and is not settled at
twenty to forty bets either — but unlike profit and loss, it
accumulates honestly and cannot be flattered by a good run. A book
that is well calibrated but unprofitable has a pricing problem it can
fix. A book that is miscalibrated is guessing, whatever the profit
looks like.

## 12. Accumulators — shadow only
No accumulators in the live book. The house margin compounds per leg
(roughly 18-20% against a four-leg accumulator at 5% overround per
leg, before either analyst forms a view), which makes it the one
product least likely to show a real edge even if one exists in the
underlying selections. For every taken single, or pair of same-day
singles, record what the accumulator equivalent would have paid, in a
shadow column, at the same prices. Twenty weeks of that data decides
whether accumulators earn a place — not before.

## 13. Boundaries
The desk researches, records and evaluates. It does not place bets
and does not hold or use bookmaker account credentials, logged in or
otherwise. Every wager is placed by the owner himself, at the price he
actually obtains at the moment of placing it — not the price showing
when the selection was made. This is a hard boundary, not a
convenience: most bookmakers prohibit automated or bot-driven account
interaction in their terms, and crossing it risks the account
regardless of who is comfortable with what.

## 14. Data sources
See `/reference/data-sources.md`. Fixtures, prices and statistics come
from public sources only — no account login is used for research.

## 15. Open items requiring owner sign-off before bet one
1. ~~Section 4 — real-money scope of the three books.~~ Decided 12
   September 2026: all three books real, £200 each, £600 total real
   exposure.
2. ~~Section 7 — the minimum edge threshold.~~ Decided 13 September
   2026: 3 percentage points.

No sections remain open. Bet one may proceed under this document as
written.
