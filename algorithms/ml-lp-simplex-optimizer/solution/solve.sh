#!/bin/bash
set -euo pipefail

cat > /app/problem.py <<'PY'
import numpy as np
from scipy.optimize import linprog

class LPProblem:
    REQUIRED = ("c", "A_eq", "b_eq", "A_ub", "b_ub", "lower", "upper")

    def __init__(self, data):
        self.c = np.asarray(data["c"], dtype=float)
        self.A_eq = np.asarray(data["A_eq"], dtype=float)
        self.b_eq = np.asarray(data["b_eq"], dtype=float)
        self.A_ub = np.asarray(data["A_ub"], dtype=float)
        self.b_ub = np.asarray(data["b_ub"], dtype=float)
        self.lower = np.asarray(data["lower"], dtype=float)
        self.upper = np.asarray(data["upper"], dtype=float)

    @classmethod
    def from_json(cls, data):
        missing = [k for k in cls.REQUIRED if k not in data]
        if missing:
            raise ValueError(f"missing required fields: {missing}")
        return cls(data)

    def validate(self):
        n = self.c.size
        if self.c.ndim != 1:
            raise ValueError("c must be one-dimensional")
        if self.A_eq.ndim != 2 or self.A_eq.shape[1] != n:
            raise ValueError("A_eq has incompatible dimensions")
        if self.A_ub.ndim != 2 or self.A_ub.shape[1] != n:
            raise ValueError("A_ub has incompatible dimensions")
        if self.b_eq.shape != (self.A_eq.shape[0],):
            raise ValueError("b_eq has incompatible dimensions")
        if self.b_ub.shape != (self.A_ub.shape[0],):
            raise ValueError("b_ub has incompatible dimensions")
        if self.lower.shape != (n,) or self.upper.shape != (n,):
            raise ValueError("bounds have incompatible dimensions")
        arrays = (
            self.c, self.A_eq, self.b_eq,
            self.A_ub, self.b_ub, self.lower, self.upper,
        )
        if any(not np.all(np.isfinite(a)) for a in arrays):
            raise ValueError("all numerical values must be finite")
        if np.any(self.lower > self.upper):
            raise ValueError("lower bound exceeds upper bound")
PY

cat > /app/optimizer.py <<'PY'
import itertools
import numpy as np
from problem import LPProblem

TOL = 2e-6


class OptimizationError(RuntimeError):
    pass


def _active_constraints(p, x):
    active = []
    g = len(p.A_ub)
    n = len(x)

    for i in range(g):
        if abs(p.A_ub[i] @ x - p.b_ub[i]) <= TOL:
            active.append(i)
    for i in range(n):
        if abs(x[i] - p.lower[i]) <= TOL:
            active.append(g + i)
    for i in range(n):
        if abs(x[i] - p.upper[i]) <= TOL:
            active.append(g + n + i)
    return active


def _constraint_rows(p, active):
    g = len(p.A_ub)
    n = len(p.c)
    rows = []
    for idx in active:
        if idx < g:
            rows.append(p.A_ub[idx])
        elif idx < g + n:
            row = np.zeros(n)
            row[idx - g] = -1.0
            rows.append(row)
        else:
            row = np.zeros(n)
            row[idx - g - n] = 1.0
            rows.append(row)
    return rows


def _feasible(p, x):
    if len(p.A_eq) and np.max(np.abs(p.A_eq @ x - p.b_eq)) > 5*TOL:
        return False
    if len(p.A_ub) and np.max(p.A_ub @ x - p.b_ub) > 5*TOL:
        return False
    return bool(
        np.min(x - p.lower) >= -5*TOL
        and np.min(p.upper - x) >= -5*TOL
    )


def solve(p: LPProblem):
    p.validate()
    n = len(p.c)

    # Enumerate active sets for small/medium benchmark instances.
    # Feasible vertices/bases are generated from equalities plus active
    # inequalities/bounds. This is intentionally self-contained.
    candidates = []

    fixed_rows = [row for row in p.A_eq]
    fixed_rhs = [v for v in p.b_eq]

    g = len(p.A_ub)
    bound_count = 2 * n
    all_ineq = list(range(g + bound_count))

    # A vertex needs enough independent active rows. We also evaluate
    # feasible points induced by subsets of all available constraints.
    needed = max(0, n - len(fixed_rows))
    subset_cap = 18
    if len(all_ineq) > subset_cap:
        raise OptimizationError("problem is too large for self-contained solver")

    for subset in itertools.combinations(all_ineq, needed):
        rows = list(fixed_rows)
        rhs = list(fixed_rhs)

        for idx in subset:
            if idx < g:
                rows.append(p.A_ub[idx])
                rhs.append(p.b_ub[idx])
            elif idx < g + n:
                j = idx - g
                row = np.zeros(n)
                row[j] = -1.0
                rows.append(row)
                rhs.append(-p.lower[j])
            else:
                j = idx - g - n
                row = np.zeros(n)
                row[j] = 1.0
                rows.append(row)
                rhs.append(p.upper[j])

        if len(rows) < n:
            continue

        M = np.asarray(rows, dtype=float)
        if np.linalg.matrix_rank(M, tol=1e-9) < n:
            continue

        try:
            x = np.linalg.solve(M[:n], np.asarray(rhs[:n], dtype=float))
        except np.linalg.LinAlgError:
            try:
                x = np.linalg.lstsq(M, np.asarray(rhs), rcond=None)[0]
            except np.linalg.LinAlgError:
                continue

        if _feasible(p, x):
            candidates.append(np.asarray(x, dtype=float))

    # Include simple bound/equality candidates for degenerate low-dimensional
    # cases by using least squares over every generated active set.
    for subset_size in range(max(1, needed - 1), min(n, needed + 1) + 1):
        for subset in itertools.combinations(all_ineq, subset_size):
            rows = list(fixed_rows)
            rhs = list(fixed_rhs)
            for idx in subset:
                if idx < g:
                    rows.append(p.A_ub[idx])
                    rhs.append(p.b_ub[idx])
                elif idx < g + n:
                    j = idx - g
                    row = np.zeros(n); row[j] = -1.0
                    rows.append(row); rhs.append(-p.lower[j])
                else:
                    j = idx - g - n
                    row = np.zeros(n); row[j] = 1.0
                    rows.append(row); rhs.append(p.upper[j])
            if len(rows) >= n:
                M = np.asarray(rows, dtype=float)
                r = np.asarray(rhs, dtype=float)
                try:
                    x = np.linalg.lstsq(M, r, rcond=None)[0]
                except np.linalg.LinAlgError:
                    continue
                if np.max(np.abs(M @ x - r)) <= 5*TOL and _feasible(p, x):
                    candidates.append(x)

    if not candidates:
        raise OptimizationError("no feasible vertex found")

    x = min(candidates, key=lambda z: float(p.c @ z))
    active = _active_constraints(p, x)
    rows = _constraint_rows(p, active)

    if rows:
        C = np.vstack([p.A_eq, np.asarray(rows)])
    else:
        C = p.A_eq

    if len(C):
        multipliers = np.linalg.lstsq(C.T, -p.c, rcond=None)[0]
        stationarity = p.c + C.T @ multipliers
        eq_mult = multipliers[:len(p.A_eq)]
        active_mult = multipliers[len(p.A_eq):]
    else:
        stationarity = p.c.copy()
        eq_mult = np.empty(0)
        active_mult = np.empty(0)

    residual = float(np.max(np.abs(stationarity)))

    if residual > 2e-6:
        raise OptimizationError(
            f"KKT stationarity residual too large: {residual}"
        )

    if np.any(active_mult < -5e-6):
        raise OptimizationError("invalid inequality multiplier sign")

    return {
        "status": "optimal",
        "x": x.tolist(),
        "objective": float(p.c @ x),
        "active_constraints": [int(v) for v in active],
        "equality_multipliers": eq_mult.tolist(),
        "inequality_multipliers": active_mult.tolist(),
        "stationarity_residual": residual,
    }
PY

echo "Reference LP implementation installed."
