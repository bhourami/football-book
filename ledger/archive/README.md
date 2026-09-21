# Era 01 — closed 21 September 2026

The staking era. Preserved exactly as it finished, including every
error and every correction. Nothing here is edited again.

## Final position

| Book | Real money? | Closing bank | Net | Bets |
|---|---|---|---|---|
| Conclusion (debated) | Yes | £194.00 | −£6.00 | 7 |
| Codex solo | Yes | £251.09 | +£51.09 | 7 |
| Cross-book accumulators | Yes | own pot | −£10.00 | 1 |
| Claude solo | Never staked | — | +£4.25 on paper | 6 |
| **Combined real money** | | | **+£35.09** | **15** |

Fifteen bets. That cannot distinguish skill from luck and was never
claimed to.

## Why it closed

Not because it was losing — it finished ahead. Because the thing it was
measuring turned out to be unmeasurable at this sample size, and the
thing that *was* measurable said the method had no edge:

- A Dixon-Coles model walked forward over **1,180 matches** beat the
  closing line about **50%** of the time. Under the live rule it would
  have staked £8,560 and lost £787.30, −9.2%.
- It selected **72.5%** of available markets. A method finding edge in
  seven matches out of ten is disagreeing with the market at random.
- Measured against margin-removed closing prices, the Matchweek 4 bets
  carried **−7.8% expected value per £10** — and the three figures were
  −0.75, −0.81, −0.78, tight enough to be a property rather than noise.

Both analysts recommended stopping on 19 September, when the books were
roughly flat. The owner actioned it on 21 September with the books
**£35.09 up**, which is the only circumstance in which honouring a
pre-commitment costs anything.

## What this era actually produced

Not profit — £35 over fifteen bets is noise. What it produced was a
documented account of how a confident method manufactures edge that
isn't there, and a record of the owner out-catching both analysts
repeatedly:

- **The Arsenal "defensive crisis"** — both models independently called
  it a crisis; Arsenal were 6-0-0 with those players already absent, and
  two of the three started.
- **The one-directional BTTS skew** — spotted across a whole gameweek
  before any model confirmed it. The finished record was 8 won, 8 lost
  from 16 selections, 15 of them "No".
- **A wrong scoreline** taken from a web fetch (1-3 against an actual
  2-3), which produced the standing rule to settle only against
  premierleague.com's own data.
- **Two Fulham picks dropped** on judgement; both would have lost.

Three numbers in this era were **typed rather than derived**, and all
three were wrong in the flattering direction: a scoreline from a fetch,
hand-maintained running totals, and the single positive CLV figure the
project ever published (recorded as a 2.80 close against a market that
actually closed at 2.98). That pattern is the most useful thing here.

## Era 02

Continues in `ledger/` under `spec/methodology.md` sections 14–18: no
stake, closing line value as the scoreboard, exchange prices as the
reference, Premier League, and a fixed decision point at 60 selections.
