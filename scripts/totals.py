"""Compute each book's running total from the ledgers. Single source of truth.

The public README used to carry hand-maintained totals, which drifted.
Anything published should come from here.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS = {"conclusion": "Conclusion (debated)",
         "claude": "Claude solo",
         "codex": "Codex solo"}
REAL = {"placed", "settled"}


def book_totals(name):
    d = json.load(open(os.path.join(ROOT, "ledger", f"{name}.json")))
    real_settled = real_open = tracked = 0.0
    n_real = n_open = n_tracked = 0
    for e in d["entries"]:
        stake = e.get("stake_gbp") or 0
        if e.get("status") in REAL:
            pl = e.get("settled_pl_gbp")
            if isinstance(pl, (int, float)):
                real_settled += pl
                n_real += 1
            else:
                real_open += stake
                n_open += 1
        else:
            pl = e.get("hypothetical_pl_gbp")
            if isinstance(pl, (int, float)):
                tracked += pl
                n_tracked += 1
    return {"bank": d.get("bank_gbp", 200), "real_settled": round(real_settled, 2),
            "n_real": n_real, "real_open_stake": round(real_open, 2),
            "n_open": n_open, "tracked": round(tracked, 2), "n_tracked": n_tracked}


def accumulators():
    d = json.load(open(os.path.join(ROOT, "ledger", "accumulators.json")))
    return round(sum(e.get("settled_pl_gbp") or 0 for e in d["entries"]), 2)


if __name__ == "__main__":
    for key, label in BOOKS.items():
        t = book_totals(key)
        staked = "REAL MONEY" if (t["n_real"] or t["n_open"]) else "tracked only"
        print(f"\n{label}  [{staked}]")
        print(f"  settled real-money P/L : {t['real_settled']:+.2f} "
              f"over {t['n_real']} bet(s)  -> bank £{t['bank'] + t['real_settled']:.2f}")
        if t["n_open"]:
            print(f"  live, unsettled        : £{t['real_open_stake']:.2f} "
                  f"across {t['n_open']} bet(s)")
        print(f"  tracked-only (paper)   : {t['tracked']:+.2f} "
              f"over {t['n_tracked']} selection(s)")
    acc = accumulators()
    print(f"\nCross-book accumulators  : {acc:+.2f}")
    combined = sum(book_totals(k)["real_settled"] for k in BOOKS) + acc
    print(f"COMBINED REAL MONEY      : {combined:+.2f}")
