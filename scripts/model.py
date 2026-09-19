#!/usr/bin/env python3
"""Dixon-Coles style Poisson model for Premier League match outcomes.

Per-team attack and defence strengths plus a home-advantage term, fitted by
maximum likelihood with exponential time decay so recent matches count more,
and the Dixon-Coles low-score correction for the 0-0/1-0/0-1/1-1 cells that a
plain independent Poisson misprices.

Pure Python -- no numpy/scipy on this machine. Analytic gradients keep the
walk-forward refitting in the backtest tractable.

    lambda_home = exp(attack[home] + defence[away] + home_adv)
    lambda_away = exp(attack[away] + defence[home])

Identifiability: mean attack is pinned to zero after each step.

Hyperparameters (decay rate, score-grid size, iteration count) are set to
literature-standard defaults and deliberately NOT tuned against the backtest
-- tuning them there would be fitting the test set and would invalidate the
result. See collaboration/debates/model-v1-backtest.md.
"""
from __future__ import annotations

import math

# Exponential time decay. Dixon-Coles used a half-life on the order of months;
# 0.0025/day gives a ~277-day half-life. Fixed default, not tuned on results.
DEFAULT_XI = 0.0025
MAX_GOALS = 10


def tau(hg: int, ag: int, lh: float, la: float, rho: float) -> float:
    """Dixon-Coles low-score correction."""
    if hg == 0 and ag == 0:
        return 1.0 - lh * la * rho
    if hg == 0 and ag == 1:
        return 1.0 + lh * rho
    if hg == 1 and ag == 0:
        return 1.0 + la * rho
    if hg == 1 and ag == 1:
        return 1.0 - rho
    return 1.0


def _dtau(hg: int, ag: int, lh: float, la: float, rho: float):
    """(d tau/d lambda_home, d tau/d lambda_away, d tau/d rho)."""
    if hg == 0 and ag == 0:
        return -la * rho, -lh * rho, -lh * la
    if hg == 0 and ag == 1:
        return rho, 0.0, lh
    if hg == 1 and ag == 0:
        return 0.0, rho, la
    if hg == 1 and ag == 1:
        return 0.0, 0.0, -1.0
    return 0.0, 0.0, 0.0


class DixonColes:
    def __init__(self, xi: float = DEFAULT_XI):
        self.xi = xi
        self.attack: dict[str, float] = {}
        self.defence: dict[str, float] = {}
        self.home_adv = 0.25
        self.rho = -0.05
        self.teams: list[str] = []
        self.n_matches = 0

    # ---------- fitting ----------

    def fit(self, matches: list[dict], ref_date=None, iters: int = 300, lr: float = 0.05):
        """Fit on `matches`. Caller is responsible for passing only matches that
        occurred strictly before the fixture being predicted -- no lookahead."""
        if not matches:
            return self
        ref_date = ref_date or matches[-1]["date"]

        teams = sorted({m["home"] for m in matches} | {m["away"] for m in matches})
        self.teams = teams
        self.attack = {t: self.attack.get(t, 0.0) for t in teams}
        self.defence = {t: self.defence.get(t, 0.0) for t in teams}
        self.n_matches = len(matches)

        weights = []
        for m in matches:
            days = (ref_date - m["date"]).days
            weights.append(math.exp(-self.xi * max(days, 0)))

        # Adam-ish: plain gradient ascent with momentum is enough and is stable
        # for this well-conditioned problem.
        va = {t: 0.0 for t in teams}
        vd = {t: 0.0 for t in teams}
        vg = 0.0
        vr = 0.0
        momentum = 0.9

        for _ in range(iters):
            ga = {t: 0.0 for t in teams}
            gd = {t: 0.0 for t in teams}
            gg = 0.0
            gr = 0.0

            for m, w in zip(matches, weights):
                h, a = m["home"], m["away"]
                hg, ag = m["hg"], m["ag"]
                lh = math.exp(self.attack[h] + self.defence[a] + self.home_adv)
                la = math.exp(self.attack[a] + self.defence[h])
                lh = min(max(lh, 1e-6), 20.0)
                la = min(max(la, 1e-6), 20.0)

                t = tau(hg, ag, lh, la, self.rho)
                if t <= 1e-9:
                    t = 1e-9
                dt_lh, dt_la, dt_rho = _dtau(hg, ag, lh, la, self.rho)

                # d/d lambda of [log tau + Poisson loglik], times d lambda/d param
                gh = (hg - lh) + (dt_lh / t) * lh
                gaw = (ag - la) + (dt_la / t) * la

                ga[h] += w * gh
                gd[a] += w * gh
                gg += w * gh
                ga[a] += w * gaw
                gd[h] += w * gaw
                gr += w * (dt_rho / t)

            n = sum(weights)
            for t_ in teams:
                va[t_] = momentum * va[t_] + (1 - momentum) * (ga[t_] / n)
                vd[t_] = momentum * vd[t_] + (1 - momentum) * (gd[t_] / n)
                self.attack[t_] += lr * va[t_]
                self.defence[t_] += lr * vd[t_]
            vg = momentum * vg + (1 - momentum) * (gg / n)
            vr = momentum * vr + (1 - momentum) * (gr / n)
            self.home_adv += lr * vg
            self.rho += lr * vr

            # identifiability + keep rho in a sane range
            mean_att = sum(self.attack.values()) / len(teams)
            for t_ in teams:
                self.attack[t_] -= mean_att
            self.rho = min(max(self.rho, -0.2), 0.2)

        return self

    # ---------- prediction ----------

    def lambdas(self, home: str, away: str) -> tuple[float, float]:
        """Unseen teams fall back to league average (attack=defence=0)."""
        ah = self.attack.get(home, 0.0)
        dh = self.defence.get(home, 0.0)
        aa = self.attack.get(away, 0.0)
        da = self.defence.get(away, 0.0)
        lh = math.exp(ah + da + self.home_adv)
        la = math.exp(aa + dh)
        return min(lh, 20.0), min(la, 20.0)

    def score_matrix(self, home: str, away: str) -> list[list[float]]:
        lh, la = self.lambdas(home, away)
        ph = [math.exp(-lh) * lh**i / math.factorial(i) for i in range(MAX_GOALS + 1)]
        pa = [math.exp(-la) * la**j / math.factorial(j) for j in range(MAX_GOALS + 1)]
        grid = [[ph[i] * pa[j] * tau(i, j, lh, la, self.rho)
                 for j in range(MAX_GOALS + 1)] for i in range(MAX_GOALS + 1)]
        total = sum(sum(row) for row in grid)
        return [[c / total for c in row] for row in grid]

    def predict(self, home: str, away: str) -> dict:
        grid = self.score_matrix(home, away)
        n = len(grid)
        home_win = sum(grid[i][j] for i in range(n) for j in range(n) if i > j)
        draw = sum(grid[i][i] for i in range(n))
        away_win = sum(grid[i][j] for i in range(n) for j in range(n) if i < j)
        btts_yes = sum(grid[i][j] for i in range(1, n) for j in range(1, n))
        over25 = sum(grid[i][j] for i in range(n) for j in range(n) if i + j >= 3)
        lh, la = self.lambdas(home, away)
        return {
            "home_win": home_win,
            "draw": draw,
            "away_win": away_win,
            "btts_yes": btts_yes,
            "btts_no": 1.0 - btts_yes,
            "over25": over25,
            "under25": 1.0 - over25,
            "lambda_home": lh,
            "lambda_away": la,
        }


def fair_probabilities(prices: list[float]) -> list[float]:
    """Strip the overround proportionally -- same method as edge_calculator.py."""
    implied = [1.0 / p for p in prices]
    total = sum(implied)
    return [i / total for i in implied]
