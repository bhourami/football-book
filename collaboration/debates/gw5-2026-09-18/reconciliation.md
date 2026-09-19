# Matchweek 5 reconciliation — 19 September 2026

## Timing note, read first

Claude's opening was sealed and committed on 15 September. Codex was then
blocked by a weekly usage-quota limit until 19 September, so true
same-day simultaneity wasn't possible this gameweek — Codex never saw
Claude's file or anything derived from it (blind sequencing held), but
the two openings are four days apart rather than minutes. Claude's
original prices are kept as the record of what Claude actually judged;
Codex was scored against fresh prices fetched on 19 September, since
Claude's file didn't record enough of the market to score Codex fairly
(only one candidate per market was ever written down, leaving several
markets with no price at all). Where both prices are known, both are
shown.

Brentford v Chelsea (18 Sept) kicked off and the odds market closed
before Codex could run. Claude had already declined it (edge -0.4%).
Codex's number (Chelsea favoured, away_win 44.6%) is recorded for the
audit trail only, unscoreable and moot — Brentford won 3-0.

## Agreed (conclusion book)

| Fixture | Market | Pick | Claude edge | Codex edge |
|---|---|---|---|---|
| Tottenham v Aston Villa | Match result | Villa win | +5.7pp | +11.4pp |
| Tottenham v Aston Villa | BTTS | No | +9.7pp | +12.1pp |
| Man City v Sunderland | BTTS | No | +10.0pp | +6.1pp |

## Disagreed or one-sided (no conclusion bet)

Full list and reasons in `collaboration/debate-conclusions.json`'s
`no_position` array. Two things worth reading in full rather than just
skimming the table:

**Brighton v Arsenal — Codex fell into the same trap Claude's original
reasoning did.** Claude declined this fixture entirely after the owner
caught a reasoning error (Arsenal are 6-0-0 this season with the exact
absence pattern that was called a "crisis" — see `CLAUDE.md`). Codex's
independent reasoning, run four days later, arrived at the identical
framing on its own: "losing three first-choice centre-backs materially
raises Brighton's scoring expectation." That's now driving *two*
Codex-solo selections (Brighton to win, +7.75pp; BTTS Yes, +7.37pp)
that rest on the same premise the owner already flagged as wrong. Both
are recorded, both are flagged — not silently let in as sound.

**Leeds v Crystal Palace — the largest edge recorded anywhere in this
project.** Codex's away-win (Crystal Palace) edge is +22.63pp, well
past Matchweek 4's Coventry-BTTS outlier (+16–24pp) that turned out to
be a genuine miscalibration warning, not a discovery. Codex's own
confidence rating on this fixture is "low." Treat this as a signal the
estimate is very likely wrong before treating it as found value.

## Volume flag — Codex-solo

Fifteen selections cleared Codex's own 3pp threshold this single
gameweek — three shared with the conclusion book, twelve Codex-solo
only. That's 75% of Codex-solo's entire 20-bet lifetime allocation in
one week, well past Matchweek 4's already-concerning 30% (six
selections). This is not evidence of a hot run of skill; it is stronger
evidence than last week that the qualitative Poisson method is running
too confident, too often, relative to a market that's actually quite
hard to beat. Recorded honestly per the fail-closed/frozen-rules
discipline — not pruned, not silently treated as safe to act on.

## Claude-solo (unchanged from the sealed opening)

Tottenham-Villa win, Tottenham-Villa BTTS No, Newcastle-Hull draw
(+5.0pp, no Codex agreement — Codex's own numbers don't clear the
threshold on any Newcastle-Hull outcome at the fresh price), Man
City-Sunderland BTTS No. Four selections, matching last gameweek's
count.
