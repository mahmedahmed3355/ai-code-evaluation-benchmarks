import json
import subprocess
from pathlib import Path

import numpy as np
import pytest
from scipy.optimize import linprog


APP = Path("/app")
CLI = APP / "cli.py"
TOL = 2e-6


def run_solver(problem, tmp_path):
    problem_file = tmp_path / "problem.json"
    output_file = tmp_path / "result.json"
    problem_file.write_text(json.dumps(problem), encoding="utf-8")

    proc = subprocess.run(
        ["python3", str(CLI), str(problem_file), "--output", str(output_file)],
        cwd=str(APP),
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert proc.returncode == 0, (
        f"solver failed\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    assert output_file.exists()
    return json.loads(output_file.read_text(encoding="utf-8"))


def reference(problem):
    c = np.asarray(problem["c"], dtype=float)
    A_eq = np.asarray(problem["A_eq"], dtype=float)
    b_eq = np.asarray(problem["b_eq"], dtype=float)
    A_ub = np.asarray(problem["A_ub"], dtype=float)
    b_ub = np.asarray(problem["b_ub"], dtype=float)
    lower = np.asarray(problem["lower"], dtype=float)
    upper = np.asarray(problem["upper"], dtype=float)

    r = linprog(
        c,
        A_ub=A_ub if len(A_ub) else None,
        b_ub=b_ub if len(b_ub) else None,
        A_eq=A_eq if len(A_eq) else None,
        b_eq=b_eq if len(b_eq) else None,
        bounds=list(zip(lower, upper)),
        method="highs",
    )
    assert r.success, r.message
    return r


def check_solution(problem, result):
    c = np.asarray(problem["c"], dtype=float)
    A_eq = np.asarray(problem["A_eq"], dtype=float)
    b_eq = np.asarray(problem["b_eq"], dtype=float)
    A_ub = np.asarray(problem["A_ub"], dtype=float)
    b_ub = np.asarray(problem["b_ub"], dtype=float)
    lower = np.asarray(problem["lower"], dtype=float)
    upper = np.asarray(problem["upper"], dtype=float)

    x = np.asarray(result["x"], dtype=float)

    assert result["status"] == "optimal"
    assert x.shape == c.shape
    assert np.all(np.isfinite(x))

    if len(A_eq):
        assert np.max(np.abs(A_eq @ x - b_eq)) <= TOL
    if len(A_ub):
        assert np.max(A_ub @ x - b_ub) <= TOL

    assert np.min(x - lower) >= -TOL
    assert np.min(upper - x) >= -TOL

    obj = float(c @ x)
    assert result["objective"] == pytest.approx(obj, rel=0, abs=TOL)
    ref = reference(problem)
    assert obj == pytest.approx(float(ref.fun), rel=0, abs=5 * TOL)

    active_ub = [
        i for i in range(len(A_ub))
        if abs(A_ub[i] @ x - b_ub[i]) <= TOL
    ]
    n = len(x)
    active_lower = [
        len(A_ub) + i for i in range(n)
        if abs(x[i] - lower[i]) <= TOL
    ]
    active_upper = [
        len(A_ub) + n + i for i in range(n)
        if abs(x[i] - upper[i]) <= TOL
    ]
    expected = active_ub + active_lower + active_upper

    actual = [int(v) for v in result["active_constraints"]]
    assert sorted(actual) == sorted(expected)

    eq_mult = np.asarray(result["equality_multipliers"], dtype=float)
    active_mult = np.asarray(result["inequality_multipliers"], dtype=float)

    assert len(eq_mult) == len(A_eq)
    assert len(active_mult) == len(expected)
    assert np.all(np.isfinite(eq_mult))
    assert np.all(np.isfinite(active_mult))

    rows = []
    for idx in active_ub:
        rows.append(A_ub[idx])
    for idx in active_lower:
        row = np.zeros(n)
        row[idx - len(A_ub)] = -1.0
        rows.append(row)
    for idx in active_upper:
        row = np.zeros(n)
        row[idx - len(A_ub) - n] = 1.0
        rows.append(row)

    if rows:
        active_matrix = np.asarray(rows, dtype=float)
        C = np.vstack([A_eq, active_matrix]) if len(A_eq) else active_matrix
    else:
        C = A_eq

    if len(C):
        multipliers = np.linalg.lstsq(C.T, -c, rcond=None)[0]
        residual = float(np.max(np.abs(c + C.T @ multipliers)))
    else:
        residual = float(np.max(np.abs(c)))

    assert residual <= TOL
    reported = float(result["stationarity_residual"])
    assert reported <= TOL
    assert reported == pytest.approx(residual, rel=0, abs=5 * TOL)

    for multiplier in active_mult:
        assert multiplier >= -TOL


CASES = [
    {
        "c": [-3.0, -2.0],
        "A_eq": [[1.0, 1.0]],
        "b_eq": [4.0],
        "A_ub": [],
        "b_ub": [],
        "lower": [0.0, 0.0],
        "upper": [10.0, 10.0],
    },
    {
        "c": [-4.0, -3.0],
        "A_eq": [],
        "b_eq": [],
        "A_ub": [[1.0, 1.0], [2.0, 1.0]],
        "b_ub": [5.0, 8.0],
        "lower": [0.0, 0.0],
        "upper": [10.0, 10.0],
    },
    {
        "c": [-5.0, -1.0],
        "A_eq": [[1.0, 1.0]],
        "b_eq": [5.0],
        "A_ub": [],
        "b_ub": [],
        "lower": [0.0, 0.0],
        "upper": [2.0, 10.0],
    },
    {
        "c": [-2.0, -5.0, -3.0],
        "A_eq": [[1.0, 1.0, 1.0]],
        "b_eq": [6.0],
        "A_ub": [[1.0, 2.0, 1.0], [2.0, 1.0, 3.0]],
        "b_ub": [9.0, 14.0],
        "lower": [0.0, 0.0, 0.0],
        "upper": [6.0, 6.0, 6.0],
    },
    {
        "c": [-6.0, -4.0, -2.0, -1.0],
        "A_eq": [[1.0, 1.0, 1.0, 1.0]],
        "b_eq": [8.0],
        "A_ub": [
            [1.0, 1.0, 0.0, 0.0],
            [0.0, 1.0, 1.0, 0.0],
            [0.0, 0.0, 1.0, 1.0],
        ],
        "b_ub": [5.0, 5.0, 5.0],
        "lower": [0.0, 0.0, 0.0, 0.0],
        "upper": [6.0, 6.0, 6.0, 6.0],
    },
]


@pytest.mark.parametrize("problem", CASES)
def test_independent_lp_verification(problem, tmp_path):
    result = run_solver(problem, tmp_path)
    check_solution(problem, result)


def test_cli_output_is_json(tmp_path):
    problem = CASES[0]
    result = run_solver(problem, tmp_path)
    assert set(result) == {
        "status",
        "x",
        "objective",
        "active_constraints",
        "equality_multipliers",
        "inequality_multipliers",
        "stationarity_residual",
    }


@pytest.mark.parametrize(
    "mutator",
    [
        lambda p: p.update({"c": [1.0, 2.0, 3.0]}),
        lambda p: p.update({"A_eq": [[1.0, 2.0, 3.0]]}),
        lambda p: p.update({"b_eq": [1.0, 2.0]}),
        lambda p: p.update({"lower": [0.0]}),
        lambda p: p.update({"upper": [0.0, 1.0]}),
        lambda p: p.update({"A_ub": [[1.0, 2.0, 3.0]]}),
        lambda p: p.update({"b_ub": []}),
    ],
)
def test_invalid_structure_is_rejected(mutator, tmp_path):
    problem = dict(CASES[0])
    mutator(problem)

    problem_file = tmp_path / "problem.json"
    output_file = tmp_path / "result.json"
    problem_file.write_text(json.dumps(problem), encoding="utf-8")

    proc = subprocess.run(
        ["python3", str(CLI), str(problem_file), "--output", str(output_file)],
        cwd=str(APP),
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert proc.returncode != 0


def test_runtime_has_no_scipy_dependency():
    source = (APP / "optimizer.py").read_text(encoding="utf-8")
    source += (APP / "problem.py").read_text(encoding="utf-8")
    assert "scipy" not in source.lower()
    assert "linprog" not in source.lower()
