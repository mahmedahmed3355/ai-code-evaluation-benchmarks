# Constrained Linear Programming Solver

Complete the LP application in `/app`.

The CLI must be:

```text
python3 /app/cli.py <problem.json> --output <result.json>
```

Solve:

```text
minimize c^T x

subject to
A_eq x = b_eq
A_ub x <= b_ub
lower <= x <= upper
```

The implementation must:

1. Validate the complete numerical structure of the input.
2. Solve feasible LPs to numerical optimality.
3. Support equalities, inequalities, lower bounds and upper bounds together.
4. Work with coupled constraints and redundant/inactive constraints.
5. Report the optimal `x` and `objective`.
6. Report all active inequalities and bounds using:
   - `i` for `A_ub[i]`
   - `len(A_ub) + i` for lower bound `i`
   - `len(A_ub) + n + i` for upper bound `i`
7. Report one equality multiplier per equality.
8. Report one multiplier per reported active inequality/bound.
9. Report a small KKT stationarity residual using:
   - `A_ub x <= b_ub`
   - `-x <= -lower`
   - `x <= upper`
10. Write the complete JSON result to the requested output file.

The runtime environment intentionally provides NumPy but does not provide SciPy. Implement the optimization logic rather than calling an external LP solver.

Do not modify `/tests`.
Do not hard-code the supplied examples.
Do not depend on state outside `/app`.
