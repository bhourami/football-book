"""Check every ledger entry against the official Premier League result.

Read-only. Reports three things:
  MISMATCH  - a recorded win/loss that the official result contradicts
  MISSING   - a completed fixture with no result recorded
  NO P/L    - a decided entry carrying no numeric profit/loss

Run this before trusting any published total. Hand-entered scorelines
have been wrong in this project before (see CLAUDE.md).
"""
import json
import os
import re
import sys

from results import results, settle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LEDGERS = ["ledger/conclusion.json", "ledger/claude.json", "ledger/codex.json"]
SKIP = {"declined", "not_placed_by_owner_choice", "withdrawn"}


def verdict(entry):
    """What the ledger currently claims: True won, False lost, None nothing."""
    for field in ("result", "hypothetical_result_if_placed"):
        val = entry.get(field)
        if isinstance(val, str):
            head = val.strip().lower()
            if head.startswith("won"):
                return True
            if head.startswith("lost"):
                return False
    return None


def main():
    res = results()
    problems = 0
    for path in LEDGERS:
        book = json.load(open(os.path.join(ROOT, path)))
        for e in book["entries"]:
            fid = e.get("fixture_id")
            if not fid or e.get("status") in SKIP:
                continue
            m = re.match(r"\d{4}-\d{2}-\d{2}-([A-Z]{3}-[A-Z]{3})$", fid)
            if not m:
                continue
            score = res.get(m.group(1))
            label = f"{path.split('/')[-1]:16} {fid:22} {e.get('selection'):11}"
            if score is None:
                continue  # not yet complete; nothing to check
            truth = settle(e.get("selection"), *score)
            if truth is None:
                print(f"?? UNKNOWN MARKET  {label}")
                problems += 1
                continue
            claimed = verdict(e)
            if claimed is None:
                print(f"MISSING   {label}  official {score[0]}-{score[1]} -> "
                      f"{'won' if truth else 'lost'}")
                problems += 1
            elif claimed is not truth:
                print(f"MISMATCH  {label}  ledger says "
                      f"{'won' if claimed else 'lost'}, official {score[0]}-{score[1]} "
                      f"says {'won' if truth else 'lost'}")
                problems += 1
            elif (e.get("settled_pl_gbp") is None
                  and e.get("hypothetical_pl_gbp") is None):
                print(f"NO P/L    {label}  {'won' if truth else 'lost'}")
                problems += 1
    print(f"\n{problems} item(s) needing attention")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
