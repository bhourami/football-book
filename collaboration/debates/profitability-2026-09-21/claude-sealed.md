> **Superseded in part, same day.** Section 2's claim that the exchange
> "takes us from losing to roughly break-even" is **wrong** — Codex
> caught it. Commission applies to net winnings, and recomputed
> properly the exchange gives −2.68% at 2% commission and −4.64% at
> 5%, not break-even. Left unedited below as the sealed record.

# Claude — sealed opening, 21 September 2026

Written and committed before seeing Codex's answer. Question from the
owner: **how do we make this work better, more efficiently, and
profitably.**

## 1. Name the constraint honestly

Profit = (our probability estimate − market's fair estimate) × stake ×
volume, minus costs. Every route to profit changes one of those terms.
Costs are the only one we have *proven* control over.

Measured: **−7.8% EV per bet** against margin-removed closing prices on
the three bets we could check. **~7% of that is venue**, not judgement.
So our judgement is worth roughly −1% against the closing line: close to
market-average, not bad. **That is the real finding and it reframes the
question** — we are not bad at this, we are average, and average loses
because of the toll.

Getting from average to profitable needs edge *strictly greater than
costs*. On an exchange that bar is ~2–5% commission on winnings. On a
bookmaker it is ~7% of everything. So:

## 2. The one certain improvement: venue

Exchange, not bookmaker. Worth +7.0% on identical calls, measured.
Requires no skill and no new insight. It takes us from losing to roughly
break-even. **It cannot by itself make us profitable** — it removes the
toll; it does not create edge.

Do this first because it is the only step whose value is already proven.

## 3. The one plausible edge: the team-news window

This is where I think the actual opportunity is, and it is the one place
where "two AIs discussing" has a structural advantage over a human
rather than a rhetorical one.

Confirmed lineups publish about **60 minutes** before kickoff. That is
genuinely new information, it arrives at a known time, and the market
reprices over minutes rather than instantly. A human reads 22 names and
forms a view in maybe ten minutes. Two models can do it in under one,
and can hold the full season's per-player context while doing it.

The hypothesis, stated so it can be killed: **the market misprices the
first few minutes after lineup publication, and a model that quantifies
lineup delta faster than the market can take the pre-adjustment price.**

Why I believe it is worth testing:
- It is the only edge available to us that does not require being
  better at football than the market in general — only faster on one
  specific, scheduled information event.
- It is exactly measurable with CLV: take the price at T+60s after
  lineups, compare to the close. No opinion required about who wins.
- The owner identified this window himself in week one.

Why it might fail: exchange liquidity in the minute after team news may
be thin; the market may already reprice in seconds via automated books;
and our pipeline latency (fetch → two models → reconcile) may exceed the
window. All three are measurable before any money moves.

## 4. Efficiency: select far less

Our selection rate was **72.5%** in backtest and 75% of a book's
lifetime allocation in one live gameweek. That is the disease, not a
side effect. A method that finds edge in seven matches out of ten has
found none.

Target: **under 5% of available markets.** If the rule does not reject
almost everything, the rule is broken. I would rather record 3
selections a month with measured CLV than 15 a week.

## 5. What I do not believe

- That a better model gets us there. We fitted Dixon-Coles properly and
  it beat the close 50% of the time over 1,180 matches. Marginal model
  improvements do not cross a 7% gap.
- That another league helps. Checked: margins are *higher* in lower
  divisions (7.34% / 8.28% / 9.28%).
- That accumulators help. They multiply the margin, once per leg.
- That more research per fixture helps. The market has already priced
  public information. Reading more of it more carefully is running
  harder in the direction the market is already standing.

## 6. The honest ceiling

Even if the team-news hypothesis works, exchange liquidity at retail
scale and 2–5% commission cap this. A genuine 3% edge on £2,000 turnover
is £60 minus commission. The intellectual result — *can two models
extract value from a scheduled information event?* — is worth more than
the money, and it should be pursued for that reason or not at all.

## 7. What I propose

1. Venue → exchange. Now. Proven +7%.
2. Score on CLV, decision point at 60 selections. Already agreed.
3. **New pre-registered experiment: the team-news window.** Capture
   exchange prices at T−65m (pre-lineup), T+1m, T+5m, T+15m and close.
   Measure whether a lineup-aware estimate beats the close. No stake.
   Costs credits and nothing else.
4. Selection rate capped at 5%. If nothing qualifies, record nothing.
