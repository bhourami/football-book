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

## Head-to-head history: check it, but don't lean on it alone

Owner-prompted, 2026-09-19: neither analyst's method was looking at
head-to-head record between the two specific teams at all. Check the
last 4-6 meetings as standard, alongside form and team news -- not as a
tie-breaker reached for after the fact. First application: Tottenham v
Aston Villa, where Villa had won 4 of the last 5 meetings.

**Correction, same day, after discussing this with Codex:** that record
was initially logged as supporting evidence for a pick. Codex's
pushback, and now the standing rule: a head-to-head pattern is only
evidence if a repeatable mechanism survives changes in manager, squad
and venue -- otherwise 4-from-5 is a small sample doing the same job
the Arsenal "crisis" narrative did, just in the other direction. Check
H2H, record it, but only let it move a probability if you can name the
mechanism that would make it repeat.

## Estimate method: the full factor set, and the discipline for using it

Owner-prompted, 2026-09-19: "think of other factors affecting football
matches... we're trying to make informed decisions from research just
like the bookies do." Discussed directly with Codex (a genuine
methodology debate, not a pick-level one). Codex's ranked list of what
a professional odds-setter actually weighs, checkable from public
sources, roughly most to least impactful for an ordinary Premier League
fixture:

1. **Underlying team strength, adjusted for opponent quality** -- not
   just table position; a run against weak opponents shouldn't outweigh
   everything known before the season.
2. **Home advantage / venue** -- already baked into most baselines;
   don't add it twice.
3. **Actual expected XI vs. what was assumed** -- the lineup check
   already does this; the largest routine adjustment, and the one place
   a real, specific, *new* fact belongs.
4. **Underlying performance beneath the scoreline** -- public xG
   (Understat), shot quality, whether results hinged on penalties/red
   cards/exceptional finishing. Refines factor 1; not a separate bonus.
5. **Rest, workload, travel, rotation risk** -- who actually played
   midweek and how many minutes, not just "they had a game."
6. **Specific tactical matchups** -- named players and mechanisms
   (e.g. "their exposed full-back vs. this winger"), not vibes.
7. **Genuine step-change** -- new manager, formation, key signing
   settling in. Needs evidence of *changed behaviour*, not just a
   headline.
8. **Scoring environment / draw propensity** -- can move the draw
   probability without changing who's "stronger."
9. **Competitive incentives** -- relegation/European stakes; usually
   minor in an ordinary midweek-table fixture.
10. **Weather/pitch** -- usually negligible.
11. **Referee assignment** -- public (premierleague.com publishes
    appointments), usually a small consideration, more relevant to
    cards/penalties than the 1X2 price.
12. **Head-to-head** -- real, but weak on its own; see above.
13. **Morale/off-field narrative** -- essentially zero weight without
    concrete, verifiable disruption. "Wanting it more" is not evidence.

**The more important rule than the list itself:** "finding another fact
is not necessarily finding another reason to change the price... broad
research, selective and explainable adjustments" (Codex's framing,
adopted here). Every fixture's reasoning should be able to say, for
each factor actually used: what the fact is, the source and date,
whether it's *new* relative to what the team has already shown, and
roughly how many points it should move the estimate -- single-digit
moves are the norm; a double-digit swing from anything other than a
major, specific lineup change demands unusually strong evidence, not a
compelling story. This is exactly what went wrong on Brighton-Arsenal
and Leeds-Crystal Palace: a narrative-sized adjustment with
results-sized evidence against it.

Public data actually available for this, corrected from an earlier
assumption that some of it wasn't: Understat (xG), football-data.co.uk
(results/odds history), and premierleague.com (referee appointments)
are all public. What's genuinely inaccessible: internal medical/training
data, private tactical plans, and bookmaker order flow. Not yet built:
an actual fitted attack/defence strength model (Dixon-Robinson-style) --
current estimates remain qualitative judgment applied to this checklist,
not a calibrated statistical model. That gap is real and should be
closed before leaning harder on this method's numbers than the
methodology's own confidence caveats already allow.

## Backlog: player props / specials markets

Owner asked about goalscorer, shots-on-target and similar specials on
19 September 2026, mid-gameweek. Explicitly out of scope for now --
`spec/methodology.md` section 1 covers only match result and BTTS, and
there is no research process, price source or edge threshold defined
for prop markets. Do not improvise a pick on request, even an
"informal" one framed as not-tracked -- if the owner wants this as a
real addition, it needs the same deliberate groundwork accumulators
got (data source, what counts as edge in a very differently-shaped
market, a real threshold), designed with no kickoff pressure, not
generated on demand minutes before a match.
