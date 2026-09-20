"""Fetch Premier League results from premierleague.com's own backing API.

Rationale in CLAUDE.md ("Settling a result"): general web fetch/search
summaries have produced plausible-but-wrong football content in this
project more than once, and the rendered matchweek page does not always
load its fixture list. This hits the same origin the site itself reads,
with no rendering layer and no model summarising a scoreline.

Only fixtures with status "C" (complete) are returned. An "L" (live)
scoreline is provisional and must never be settled against.
"""
import json
import urllib.request

API = "https://footballapi.pulselive.com/football/fixtures"
COMP_SEASON = 841  # 2026/27; see /football/competitions/1/compseasons
HEADERS = {
    "Origin": "https://www.premierleague.com",
    "Referer": "https://www.premierleague.com/",
    "Account": "premierleague",
    "User-Agent": "Mozilla/5.0",
}

# premierleague.com club names -> the three-letter codes used in fixture_ids
CODES = {
    "Arsenal": "ARS", "Aston Villa": "AVL", "Bournemouth": "BOU",
    "Brentford": "BRE", "Brighton & Hove Albion": "BHA", "Chelsea": "CHE",
    "Coventry City": "COV", "Crystal Palace": "CRY", "Everton": "EVE",
    "Fulham": "FUL", "Hull City": "HUL", "Ipswich Town": "IPS",
    "Leeds United": "LEE", "Liverpool": "LIV", "Manchester City": "MCI",
    "Manchester United": "MUN", "Newcastle United": "NEW",
    "Nottingham Forest": "NFO", "Sunderland": "SUN",
    "Tottenham Hotspur": "TOT",
}


def fetch(page_size=120):
    url = f"{API}?comps=1&compSeasons={COMP_SEASON}&page=0&pageSize={page_size}&sort=asc&statuses=C"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["content"]


def results():
    """{'<HOME>-<AWAY>': (home_goals, away_goals)} for completed fixtures."""
    out = {}
    for m in fetch():
        if m.get("status") != "C":
            continue
        home, away = m["teams"]
        try:
            key = f"{CODES[home['team']['name']]}-{CODES[away['team']['name']]}"
        except KeyError as exc:
            raise SystemExit(f"unmapped club name {exc} -- add it to CODES") from exc
        out[key] = (int(home["score"]), int(away["score"]))
    return out


def settle(selection, home_goals, away_goals):
    """True if `selection` won, False if it lost, None if not a known market."""
    if selection == "home_win":
        return home_goals > away_goals
    if selection == "away_win":
        return away_goals > home_goals
    if selection == "draw":
        return home_goals == away_goals
    if selection == "btts_yes":
        return home_goals > 0 and away_goals > 0
    if selection == "btts_no":
        return not (home_goals > 0 and away_goals > 0)
    return None


if __name__ == "__main__":
    for k, (h, a) in sorted(results().items()):
        print(f"{k}  {h}-{a}")
