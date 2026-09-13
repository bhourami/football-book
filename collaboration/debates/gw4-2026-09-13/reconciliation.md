# Matchweek 4 reconciliation — 13 September 2026

Mechanical rule (PROTOCOL.md): a bet enters the **conclusion** book only when
both analysts' final decision agrees on market and selection, and neither
is blocked by fail-closed. Disagreement — including "one took it, one
declined it" — is preserved as no position, never merged or averaged.

Edges below are edge = our probability − fair probability (market price,
overround removed), against the same Bet365 line both analysts were scored
against.

## Coventry City v Brighton (14:00, 13 Sep)

| Market | Claude | Codex | Agree? | Conclusion |
|---|---|---|---|---|
| Draw | taken, edge +3.5pp | taken, edge +4.8pp | yes | **TAKE — draw** |
| BTTS No | declined (edge +23.8pp, flagged implausible) | taken, edge +16.4pp | no | NO POSITION |

## Manchester United v Manchester City (16:30, 13 Sep)

| Market | Claude | Codex | Agree? | Conclusion |
|---|---|---|---|---|
| Man City to win | declined, edge +0.7pp | taken, edge +11.7pp | no | NO POSITION |
| BTTS No | taken, edge +6.5pp | taken, edge +5.9pp | yes | **TAKE — BTTS No** |

## Leeds United v Newcastle United (20:00, 14 Sep)

| Market | Claude | Codex | Agree? | Conclusion |
|---|---|---|---|---|
| Newcastle to win | taken, edge +3.4pp | taken, edge +11.2pp | yes | **TAKE — Newcastle win** |
| BTTS No | declined, edge +2.1pp (below threshold) | taken, edge +3.6pp | no | NO POSITION |

## Notes

- Claude declined Coventry–Brighton BTTS No despite the math clearing the
  threshold, on the stated ground that a 24-point disagreement with a liquid
  market from an unvalidated qualitative method is more likely a modelling
  error than a real edge. Codex's independent estimate landed in the same
  direction from a stated expected-goals/Poisson method, at a smaller but
  still large magnitude (+16.4pp). This is corroborating in direction but
  not fully independent evidence — both analysts reasoned from the same
  supplied team-news facts, not separately sourced research, so agreement
  here is weaker evidence than it would be from genuinely separate inputs.
  Per the frozen rule against revising a position after seeing the result,
  Claude's decision was not changed on seeing Codex's number.
- Codex's solo book, taken at face value, would place **six** bets from a
  single gameweek (all three fixtures, both markets each) — 30% of its
  entire 20-bet lifetime allocation in one week. That volume of
  double-digit-point edges from one gameweek is itself a soft signal worth
  the owner's attention: it is more consistent with an uncalibrated model
  running hot than with a real, sustained edge in a competitive market.
  Flagged, not acted on — nothing in the frozen methodology caps bets per
  gameweek, and this session will not invent one.
