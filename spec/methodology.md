# Football Book — Frozen Methodology
Version: V1
Frozen: 12 September 2026
Last amended: 19 September 2026 (section 7: BTTS market paused pending
a real data-grounded model)
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

**BTTS market paused, 19 September 2026, owner's call.** Across every
Matchweek 5 fixture where either analyst took a BTTS position (9 of 9
for Codex, 2 of 2 taken for Claude), the "No" side's own estimated
probability came out higher than the market's fair "No" probability —
every single time, regardless of the specific matchup. That is not
fixture-specific value-finding; it is a systematic skew, shown
independently by two separately-built methods, almost certainly because
neither is grounded in real scoring data — "expected goals" in the
current method is a qualitative guess per fixture, not computed from
actual goals-scored/conceded. **No new BTTS selection may be taken by
either book until the estimate method for this market is rebuilt on
real data** (actual season goals for/against, or real xG from
Understat — see `/reference/data-sources.md`) and shown not to produce
this pattern. Match-result selections are not paused, but should be
read with the same skepticism until the same grounding exists there
too. This is a pause on new selections, not a reason to reopen or
retroactively decline what's already been staked — those stand,
recorded honestly, and settle on their actual results.
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

## 12. Accumulators — decided
Originally frozen as shadow-only: no accumulators in the live book,
because the house margin compounds per leg (roughly 18-20% against a
four-leg accumulator at 5% overround per leg, before either analyst
forms a view), making it the product least likely to show a real edge
even if one exists in the underlying selections. That reasoning stands
and is not deleted — an accumulator is still a much harder bar to
clear than any single leg.

**Amended 13 September 2026, owner's call: accumulators are now
permitted in the live book**, at the owner's discretion, under these
rules:
- An accumulator may only combine selections that a single book
  (Claude-solo, Codex-solo, or conclusion) has itself already taken
  as its own selections that gameweek — never a mix pulled from
  different books, and never a selection any book declined.
- Staked separately from the singles (its own flat £10 stake),
  charged against that book's own bank, and counted as one additional
  bet toward that book's 20-bet ceiling and bet-10 review checkpoint.
- Recorded as its own entry, showing every leg's price and the
  combined price, never merged into the single-selection rows.

**Amended again 19 September 2026, owner's call: a cross-book
accumulator is now also permitted.** The single-book restriction above
is relaxed, not removed — every leg must still be a selection some
book actually took (cleared the threshold, wasn't declined); the
change is that those legs no longer need to come from the same book.
Owner's stated reasoning: every leg is already research-backed
regardless of which book took it, so the book boundary doesn't add
anything the underlying research process didn't already provide.
- A cross-book accumulator is tracked in its own record
  (`ledger/accumulators.json`), not charged against any single book's
  £200 bank or 20-bet ceiling — it draws on selections already scored
  under their own book, so counting it against one book's bank would
  attribute exposure to a book that didn't choose it alone.
- Still not itself edge-gated (no combined-edge threshold exists —
  see below), still its own flat £10 stake, still recorded with every
  leg's price and the combined price.

**OPEN — no combined-edge threshold is defined for accumulators.**
Section 7's 3pp threshold gates each single leg's *individual*
selection, not the combined accumulator price. Until this is set, an
accumulator is a discretionary bonus bet layered on top of selections
that already cleared the single-leg threshold on their own — not
itself a modelled, edge-gated selection. Do not treat an accumulator
being placed as evidence the process endorses its combined price.

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

---

# Amendment, 21 September 2026 — the pivot

Decided by the owner after the September findings. This supersedes the
staking sections above where they conflict. Everything not restated here
still stands, including section 13's hard boundary.

## 14. Staking is suspended

**No further stake is placed under the model-driven selection rule.**
Both analysts recommended this independently on 19 September, when the
books were roughly flat. It is being actioned on 21 September with the
books **£35.09 up**, which is the only circumstance in which honouring a
pre-commitment actually costs anything and therefore the only
circumstance in which it means anything.

The two real-money books close here:

| Book | Closing bank | Net | Bets |
|---|---|---|---|
| Conclusion (debated) | £194.00 | −£6.00 | 7 |
| Codex solo | £251.09 | +£51.09 | 7 |
| Cross-book accumulators | own pot | −£10.00 | 1 |
| **Combined** | | **+£35.09** | **15** |

Fifteen bets cannot distinguish skill from luck and are not claimed to.

### Why, in one number

Measured against the **margin-removed closing price** — the best
available estimate of true probability — the three Matchweek 4
match-result bets carried an expected value of **−7.8% per £10 staked**:

| Bet | Taken at | Fair closing price | EV per £10 |
|---|---|---|---|
| Coventry v Brighton, Draw | 3.70 | 4.00 | −£0.75 |
| Leeds v Newcastle, Newcastle | 2.90 | 3.16 | −£0.81 |
| Man Utd v Man City, Man City | 2.15 | 2.33 | −£0.78 |

Note how tight those three are. That is not variance, it is a stable
property of the method, and it agrees with the walk-forward backtest's
realised −9.2% over 1,180 matches. Two independent measurements, the
same answer.

## 15. The scoreboard is closing line value, not profit

Profit is not the measure of whether this works, and never was a usable
one: separating a real edge from luck through P&L needs hundreds of
bets. CLV is measured on every selection against a continuous number,
so it converges in tens.

**CLV is not a proxy for edge. Measured against the margin-removed
closing price, it is the edge**, expressed as expected value. A
selection with positive CLV makes money in the long run whether or not
it wins; a selection with negative CLV loses money in the long run
however often it wins.

Recorded for every selection, staked or not:

- price available at decision time, timestamped
- margin-removed fair price at the close, from
  `data/E0_<season>.csv` or a timestamped capture — **never typed by
  hand** (see CLAUDE.md, 21 September)
- CLV in percentage points, and EV per £10

**Decision point, fixed now:** after **60 selections**, if median CLV is
at or below zero, the conclusion is that this method cannot price
football better than the market, and the project stops looking for edge.
No extension, and no early stop because a run of results looks good.

## 16. Venue: exchange, not bookmaker

Where a price is recorded for comparison, the reference venue is a
betting **exchange** (Betfair, Matchbook, Smarkets), not a sportsbook.

A bookmaker builds 5–7% margin into the quoted price. An exchange
charges commission on **net winnings only**, typically 2–5%, and nothing
when a selection loses. On the three Matchweek 4 selections the same
opinions were worth **+7.0% on average** at the exchange:

| Selection | Bookmaker | Exchange | |
|---|---|---|---|
| Coventry v Brighton, Draw | 3.70 | 3.90 | +5.4% |
| Leeds v Newcastle, Newcastle | 2.90 | 3.15 | +8.6% |
| Man Utd v Man City, Man City | 2.15 | 2.30 | +7.0% |

**CORRECTED the same day, by Codex.** The first version of this section
said the ~7% was "close to the entire −7.8% expected loss" and took us to
roughly break-even. **That was wrong.** Commission applies to net
winnings, so the effective price is `1 + (odds − 1) × (1 − commission)`,
and it must be applied before computing EV. Recomputed on the same three
selections:

| Commission | Mean EV per bet |
|---|---|
| Bookmaker (baseline) | −7.80% |
| Exchange at 2% | **−2.68%** |
| Exchange at 5% | **−4.64%** |

The exchange recovers 5.1pp at 2% commission and 3.2pp at 5%. **It
remains negative at both.** Moving venue makes the method lose less; it
does not make it break even, and it certainly does not make it
profitable.

This raises the bar rather than lowering it: to break even on the
exchange we now need demonstrated edge of **at least 2.7pp** against the
closing line, not zero. Nothing in this project's history suggests we
have it.

A second caveat on that "+7%": it compares a bookmaker price taken at
decision time against an exchange price at the *close*, so it conflates
venue with timing. Measured at a single instant during the 20 September
capture (Ladbrokes 3.40/3.70/2.00 against exchange 3.70/3.95/2.06) the
pure venue effect is about **+6.2%**. The conclusion is unchanged.

Exchanges also do not restrict winning accounts. A bookmaker detects a
sharp bettor precisely by positive CLV, so on a sportsbook, succeeding
at section 15 leads to restriction rather than profit.

## 17. Competition stays the Premier League

Checked on 21 September rather than assumed, across full fixture lists:

| League | Median bookmaker margin | Median books |
|---|---|---|
| Premier League | **7.34%** | 10.5 |
| Championship | 8.28% | 8.0 |
| League Two | 9.28% | 12.0 |

Lower divisions are **more expensive, not less**. The folk belief that
they are softer is half true — they are priced less accurately — but the
bookmaker compensates with a wider margin precisely because it is less
confident. Moving down would require being about 2pp *more* accurate
than the market just to stand still, in competitions we know less well,
with a thinner consensus benchmark and thinner exchange liquidity.

There is also no reason to believe a method that cannot price the
Premier League can price the Championship. **Revisit only if section 15
returns positive median CLV** — at which point "is the edge larger where
the market is softer?" becomes a real question with a real prior.

## 18. Stake size

Unchanged and not up for discussion while CLV is unproven. Stake
multiplies whatever edge exists: at −7.8%, a £2,000 bank loses £156 per
turnover where a £200 bank loses £15.60. **Stake is revisited only after
median CLV over 60+ selections is positive**, and then on the measured
size of the edge, never on how a recent run has felt.

