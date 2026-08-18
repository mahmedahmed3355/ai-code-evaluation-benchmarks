
from problem import LPProblem

TOL = 2e-6


class OptimizationError(RuntimeError):
    pass


def solve(problem: LPProblem):
    problem.validate()

    # TODO:
    # Implement a self-contained LP solver for small/medium numerical LPs.
    #
    # Required behavior:
    # - equalities, inequalities, lower/upper bounds
    # - optimal feasible solution
    # - active constraint indexing
    # - equality and active inequality/bound multipliers
    # - KKT stationarity residual
    #
    # The runtime image intentionally contains only the required numerical runtime.
    raise NotImplementedError("LP optimization is incomplete")
