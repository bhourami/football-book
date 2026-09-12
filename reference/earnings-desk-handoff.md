# Starting a football book: what to carry over, and what not to

Written 12 September 2026 from the earnings desk, to be dropped into the first
message of the new thread so it starts with what this one paid to learn rather
than rediscovering it over a fortnight.

## The honest assessment first

The machinery transfers well. The product does not.

**What makes football a better fit than earnings, genuinely.** Kick-off is an
unambiguous, published, hard cutoff — no announcement-timing verification, which
was the single largest blocker here and left 1,228 of 1,232 names unactionable.
The fixture list is a natural frozen universe. Outcomes settle in ninety minutes
rather than waiting on a close, so a hundred results take weeks, not years, and
a hundred results is roughly where any of this starts to mean anything. The data
is better and cheaper than financial data: football-data.co.uk, FBref, Understat
for xG, API-Football for fixtures and odds, mostly free.

**What makes the accumulator the wrong instrument.** The bookmaker's margin is
built into every price, typically 5–7% per market, and on an accumulator it
compounds per leg. Four legs at 5% overround is roughly 18–20% against you
before anyone forms a view. That is not a cost like a spread; it is the house's
edge, guaranteed, and it does not average out.

Set that beside what the earnings book measured last week. Four wins in ten and
it still lost money, because the average loss was 3.62 times the average win —
a payoff needing a 78% hit rate to break even. An accumulator is deliberately
built to have a low hit rate and a large payout, which is that same shape,
worsened on purpose, with a compounding house margin on top.

So the accumulator is the one product where two good analysts arguing carefully
would be least likely to show up in the results. Any edge has to clear 20% before
it registers. **Singles, or doubles at most, test the identical question with a
fifth of the drag.** If the aim is to find out whether this process produces
edge, run singles and record what the accumulator version of the same selections
would have returned — the comparison is free and it answers both questions.

The other thing equities do not have: a counterparty who can refuse you. A
bettor who wins gets limited or closed. That belongs in the plan from the start,
not as a surprise later.

## Carry these over unchanged

They are the parts that cost the most to get right here.

- **Blind before debate.** Each analyst's selection sealed before it sees the
  other's. In this repo Claude opened against an empty transcript while Codex's
  first turn already contained Claude's, so the "Codex solo" book was really
  Codex reacting to Claude and the comparison flattered the debate. Fix that on
  day one; it is invisible afterwards.
- **Three books.** Claude alone, Codex alone, and the debated conclusion, each
  with its own bank, scored on identical selections at identical prices. It is
  the only way to learn whether the arguing is worth its cost.
- **Fail closed.** A missing input is never a zero. No team news, no bet.
- **Frozen rules.** Write the staking, selection and settlement rules once,
  before the first bet, and never edit them to fit a result. Conflicts get
  raised, not resolved quietly.
- **A rejected-selection audit.** Score what you declined on the same dates.
  Here the leading book leads entirely on two refusals; without that audit the
  reason would have been invisible.
- **Record the price you actually got**, with source and timestamp, at the
  moment of selection. Odds move. A price recalled afterwards is not evidence.

## Do these differently

- **Track closing line value from the first bet.** Whether your price beat the
  closing price is the single best early indicator in betting, and it tells you
  something after twenty bets rather than two hundred. Equities have no clean
  equivalent; this is the one place football is easier to evaluate.
- **Log the overround per market** so the drag is measured, not assumed.
- **Stake flat.** The earnings book put nearly everything at the same floor by
  accident, which meant conviction was never expressed and never tested. Do it
  deliberately instead: flat stakes until there is evidence that sizing adds
  anything.
- **Decide up front whether this is paper or real.** The equities pot is
  notional, and that removes a whole class of pressure. Real money changes the
  correct answer to almost every design question below it.

## Real money: £200, and what it can and cannot answer

Decided 12 September 2026. Real, not notional, and the owner wants stakes that
matter rather than token amounts. Both are his call. What follows is the
arithmetic that call runs into, because the point of the desk is to say so
before rather than after.

**Bank life is stake size, not time.** £200 at £25 a bet is eight bets. At £20
it is ten. A losing run of eight at odds around 3.00, where roughly one in three
lands, is entirely ordinary -- not bad luck, the expected shape of the
distribution. So "a few weeks" and "not playing for pennies" are in direct
tension: at meaningful stakes this bank can be gone inside one weekend, with
nothing learned either way. £10 a bet gives twenty bets and two to three weeks
of selective Premier League singles, which is the honest reconciliation of the
two wishes. Higher odds shorten it further, because a lower strike rate means
longer losing runs.

**Twenty to forty bets cannot separate skill from luck on profit and loss.** It
is not close. If the bank finishes up he will conclude the system works and if
it finishes down he will conclude it does not, and neither conclusion would be
supported by the sample. That failure of inference is the specific thing this
whole project was built to avoid, and real money makes it more tempting, not
less.

**So judge it on closing line value instead.** Whether the price obtained beat
the closing price is measurable per bet, carries signal at twenty to thirty
bets where profit and loss needs hundreds, and cannot be faked by a good run.
Beating the close consistently is evidence of edge even while losing money;
losing to the close while winning money is evidence of luck. Record CLV on
every bet from the first one and treat it as the primary metric, with profit
and loss as a diagnostic. That is the direct equivalent of section 14's
benchmark-relative expectancy, which the equities book already treats as
primary over absolute profit and loss.

**Set the stop before the first bet, as a rule rather than an intention.**
Section 19 of the frozen equities methodology is the precedent and it was
written by the owner for himself: a hard cap per execution, a hard maximum
number of executions, terminating early if any decision is altered because of
the live account's P/L, stopping automatically at the limit, and never rolled
forward because it is winning. Copy that shape. A bank, a maximum number of
bets, a review point, and the same termination clause -- the moment a selection
or a stake changes because of what the account is showing, the experiment has
stopped measuring what it was built to measure and should end.

**Boundaries.** The desk researches, records and evaluates. It does not place
bets and does not touch account credentials; every wager is placed by the owner
himself. Odds obtained are recorded from what he actually got, not from what
was showing when the selection was made.

## Two questions the owner asked, answered before they cost anything

**Can the bets be automated?** No, on two independent grounds. The desk does not
place wagers or hold account credentials; every bet is placed by the owner. And
separately, nearly every bookmaker prohibits automated or bot-placed betting in
its terms, so building it would risk the account regardless of who is
comfortable with what. Selection, pricing, recording and evaluation are all
automatable; the placement is not.

**Is football riskier because of upsets?** The instinct is right and the reason
is wrong, and the distinction changes what to guard against.

Upsets are not the risk, because they are priced. A 1.20 favourite loses roughly
one time in six and the price already says so. Unpredictability only costs money
when the price is wrong, and on that measure football is better served than
earnings: thousands of matches a season, stable base rates, xG, team news, and a
liquid market aggregating all of it. Earnings offers one observation per company
per quarter, and section 11's implied move could not be obtained at all.

The real difference is that **every bet is all-or-nothing**. The worst earnings
loss on this desk was NAVN at minus 21.75% of the position. A losing single is
minus 100% of stake, settled, with nothing left to recover. That is roughly five
times the per-bet variance the equities book has been running, and it is the
actual reason a £200 bank is fragile -- not upsets.

The structural difference sits underneath both. Equities are positive-sum and
drift upward, so an unskilled participant still earns something over time.
Betting is negative-sum by construction: the overround means every bet starts
behind, and skill has to clear that before it is worth anything at all.

## The one check to build before the first real bet

The football equivalent of the expectation bar. Cheap to build, and it is the
difference between betting on opinions and betting on prices.

**Every price states a strike rate.** Strip the margin out and the implied
probability is the bookmaker's estimate of how often the thing happens. There is
no bet unless our own estimate differs from it, and differs by more than the
margin. A team can look excellent and still not be a bet, because the price
already says it is excellent.

    implied probability   = 1 / decimal odds
    overround             = sum of implied probabilities across the market, minus 1
    fair probability      = implied / (1 + overround)      [proportional method]
    edge                  = our probability - fair probability
    break-even strike     = fair probability

Because a losing single is minus 100% of stake, the strike rate required moves
sharply with the price. At 2.00 it is better than 50%, at 3.00 better than 33%,
at 5.00 better than 20%. Longer odds are not free: they buy a larger payout by
requiring us to be right about a rarer thing, and the bank must survive the
longer gaps between wins. Record the required strike rate on the selection card
next to the one we claim, so the two are always read together.

**Where our probability comes from, and where it must not.** From a stated
model with a written method -- base rates, xG-derived expectations, home
advantage, availability -- fitted before the fixture and not adjusted after
seeing the price. Anchoring an estimate to the odds and then declaring an edge
is the easiest self-deception available here and it produces a book that always
agrees with itself. If no honest independent estimate can be formed, that is a
no-bet under the fail-closed rule, exactly as a blocked critical input forces £0
on the equities desk.

**Calibration is the thing to track, not the edge claim.** Bucket every claimed
probability and compare it against realised frequency: of the selections given
roughly 60%, did about 60% land? A book that is well calibrated but unprofitable
has a pricing problem it can fix. A book that is miscalibrated is guessing, and
its edge numbers mean nothing however good the profit looks. Twenty to forty
bets will not settle calibration either, but it accumulates from the first bet
and cannot be flattered by a good run.

**Selection rule, stated once and frozen.** No bet unless the edge clears a
stated threshold after the margin is removed -- a floor, not a preference -- and
the required strike rate, the claimed strike rate, the price obtained and the
overround are all recorded before kick-off. Every rejected selection carries the
same fields, so the rejected-selection audit can ask later whether the threshold
was set in the right place.

## Four process lessons, learned expensively

1. **Component tests are not end-to-end verification.** Thirteen passing unit
   tests were reported here as a verified funding path. It had never once run,
   and when it did it could not have worked.
2. **Silence looks like success.** A step that reported "prepared 1 job" had
   prepared none. Anything that can do nothing must say so loudly.
3. **A shared spec beats two clever agents.** Most wasted effort here was two
   agents building the same thing twice, in parallel, slightly differently.
   Agree who owns what before either starts.
4. **Write down what cannot be bought back.** Odds at selection time, team news
   as it stood, the closing price. None of it can be reconstructed later, and
   the equivalent omission here cost a fortnight of estimate history.

## Suggested first version

One league. Premier League only. Singles on match result and both-teams-to-score,
flat two-unit stakes from a notional bank, two analysts blind then debating,
three books, closing line value logged on every bet, and a rejected-selection
audit. No accumulators in the live book — record what they would have paid, in a
shadow column, and let twenty weeks of data decide whether they earn a place.

Expand to a second league only once a hundred settled bets exist. Coverage was
never the constraint here; deciding well and recording honestly was.
