# Data sources

Public sources only. No bookmaker account login is used for research or
pricing — see methodology section 13 and CLAUDE.md's hard boundary.

- **football-data.co.uk** — historical results and closing/opening odds
  (CSV, free). Good for base rates and backtesting the edge model; not live.
- **FBref** (via Sports Reference) — match stats, team and player data, free
  to browse; check their usage/scraping terms before any automated pull.
- **Understat** — expected goals (xG) and expected points, free; used for the
  our-probability model's xG-derived component (methodology section 7).
- **API-Football** — fixtures, live and pre-match odds across bookmakers,
  free tier available. Primary source for the "price obtained" and
  "overround" fields on the selection card, and for closing-price capture
  (CLV, methodology section 10).

None of these require, or should ever be given, the owner's bookmaker
credentials. If a source's free tier is insufficient for a given need, that
is a decision for the owner (new API key, paid tier) — not something to work
around with scraping a logged-in account.
