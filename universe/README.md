# Universe

One frozen fixture-list snapshot per Premier League gameweek:
`<season>-gw<NN>.json`, written before any selection work starts for that
gameweek, and never edited afterwards. Amendments (postponements,
rearrangements) go to `amendments.json` with reason and timestamp — the
original snapshot file is never edited in place.

Each fixture entry:

```json
{
  "fixture_id": "2026-09-19-ARS-MCI",
  "competition": "Premier League",
  "gameweek": 5,
  "kickoff_utc": "2026-09-19T14:00:00Z",
  "home_team": "Arsenal",
  "away_team": "Manchester City"
}
```

The fixture list is the frozen universe (handoff doc: "unambiguous, published,
hard cutoff" — kick-off, not an announcement window that needs verifying).
