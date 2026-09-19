# football-book

This repository runs a real-money football betting research pipeline: three
parallel books (Claude alone, Codex alone, debated conclusion) tested against
identical Premier League singles at identical prices, evaluated primarily on
closing line value rather than profit and loss. It is the sequel to
`~/earnings-lab`, carrying over what that project paid to learn — see
`/reference/earnings-desk-handoff.md` for the source document.

## Authoritative methodology

`/spec/methodology.md` is the **authoritative rule set** for this project. It
defines the bank, stake, stop rule, market scope, the blind-before-debate
protocol, the edge/selection formulas, the selection card schema, the
rejected-selection audit, and CLV/calibration tracking.

- **Every session must read `/spec/methodology.md` at the start of the
  session**, before writing or modifying any code, data, or reports.
- **No session may change or reinterpret any definition in
  `/spec/methodology.md`.** It is filled in and maintained by the owner only.
  Do not "fix", "clarify", "infer a reasonable default for", or silently work
  around a gap or ambiguity in it — including the sections currently marked
  **OPEN**.
- Sections marked OPEN in the methodology are not decided. No bet may be
  entered into the live book while a section it depends on is still OPEN.
  Flag it; do not guess a number and proceed.
- If anything in the codebase, a request, or the data appears to **conflict**
  with `/spec/methodology.md` — that is an error to raise to the owner, not a
  decision to resolve unilaterally.

## Hard boundary

No session, script or agent in this repository places a bet, or holds, reads,
or uses bookmaker account credentials, ever — see methodology section 13. All
research, pricing and recording here is done from public data sources. The
owner places every wager himself, at the price he actually obtains.

## Repository layout

- `/spec/` — frozen methodology and other authoritative specifications.
- `/reference/` — data source notes and the earnings-desk handoff document
  this project started from. Non-authoritative for rules; never a substitute
  for `/spec/methodology.md`.
- `/universe/` — frozen fixture-list snapshots (one per gameweek).
- `/collaboration/` — the blind-before-debate protocol and each analyst's
  input files.
- `/ledger/` — the three books' selection cards and settled results.
- `/requests/` — the rejected-selection audit.
- `/scripts/` — pipeline code (edge/CLV calculator, etc).

## Analyst handoff

- `/collaboration/claude-input.json` and `/collaboration/codex-input.json`
  hold each analyst's current selections. Claude writes only its own file;
  Codex writes only its own. Neither reads the other's file, or any content
  derived from it, before its own opening selection for a fixture is written
  and committed to disk.
- Read `/collaboration/PROTOCOL.md` before performing any selection or debate
  work. It exists specifically to prevent the sequencing bug that flattered
  an earlier "solo" book by letting it react to the other analyst's opening
  view without either the owner or the analysts noticing.
- Ledger figures asserted in an input file are claims, not entries. A bet
  enters `/ledger/` only with a completed selection card: price, source,
  timestamp, and (once placed) the price the owner actually obtained.

## Fail-closed

No team news, no bet. Missing or unconfirmed inputs are never defaulted to a
selection — see methodology section 6. This applies identically to the
rejected-selection audit: a decline for insufficient evidence is recorded
with the same fields as a taken bet.

## Bookmaker UI risk

On Matchweek 4's first placements, the owner ended up on something he didn't
mean to -- a "2Up&Win - Early Payout" enhanced single instead of the plain
market, and an odds boost applied without realising what it was -- one
mishap, not two separate ones. Recorded honestly as accidental rather than
presented as a considered decision. When recording
`price_obtained_by_owner`, if the product, price or structure looks unusual
next to what was modelled, ask rather than assume it was intentional.

## Injury lists need a form check, not just a headcount

On Matchweek 5, Brighton v Arsenal's Draw pick was built on "Arsenal
missing three first-choice central defenders -- a genuine defensive
crisis." The owner caught what the process should have: Arsenal were 6
wins from 6 in all competitions with that same absence pattern already
in place (Saliba out long-term since before the season started, Timber
out for most of those wins, Mosquera's absence also mid-run). An injury
list is only decision-relevant if it's *new* relative to what the team
has already shown it can do without those players. Before treating any
absence as a "crisis" or a material factor, check the team's actual
recent results with the current lineup situation, not just the list of
names. See `collaboration/claude-input.json` (2026-09-19-BHA-ARS) and
`requests/rejected-selections.json` for the correction.

Same fixture, same gameweek: Codex's independent analysis (genuinely
blind to Claude's correction) reproduced the identical "defensive
crisis" framing on its own. Two independent analysts made the same
category of mistake, which means it isn't a one-off slip -- it's a gap
in how both methods use an injury list. Check the actual league table
(position, points, recent results) for every fixture with an
absence-based argument, not just the ones where the owner happens to
follow a team closely enough to catch it personally.

The same gameweek surfaced a second gap: the same failure pattern
("large claimed edge on the underdog") also showed up on Leeds v
Crystal Palace (Codex backed 16th-place, one-win-in-four Palace to beat
an unbeaten 4th-place Leeds at +22.6pp, the largest edge recorded in
this project) and, to a lesser extent, Fulham v Man Utd. Large edges on
a team that's clearly struggling in the table deserve the same
scrutiny as a "crisis" injury narrative -- both are ways of overriding
what the season has actually shown with a story that sounds compelling
in isolation.

## Head-to-head history is a real input, not checked yet

Owner-prompted, 2026-09-19: neither analyst's method currently looks at
head-to-head record between the two specific teams at all -- only
current-season form and team news. History matters in football (a team
that has a specific hoodoo over an opponent, or dominates a fixture
regardless of league position, is a real and common pattern). Check the
last 4-6 meetings between the two sides as a standard part of forming
the pre-match estimate, alongside form and team news -- not as a
tie-breaker only reached for after the fact. First application:
Tottenham v Aston Villa (see `collaboration/claude-input.json`) --
Villa have won 4 of the last 5 meetings, which turned out to support
the pick already made rather than contradict it, but the process should
have looked regardless of which way it cut.
