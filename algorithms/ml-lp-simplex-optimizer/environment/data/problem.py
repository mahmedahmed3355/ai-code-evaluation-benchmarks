import numpy as np


class LPProblem:
    REQUIRED = (
        "c",
        "A_eq",
        "b_eq",
        "A_ub",
        "b_ub",
        "lower",
        "upper",
    )

    def __init__(self, data):
        self.c = np.asarray(data["c"], dtype=float)
        self.A_eq = np.asarray(data["A_eq"], dtype=float)
        self.b_eq = np.asarray(data["b_eq"], dtype=float)
        self.A_ub = np.asarray(data["A_ub"], dtype=float)
        self.b_ub = np.asarray(data["b_ub"], dtype=float)
        self.lower = np.asarray(data["lower"], dtype=float)
        self.upper = np.asarray(data["upper"], dtype=float)

        n = self.c.shape[0]

        # Empty constraint sets are valid and must still have
        # a two-dimensional matrix representation.
        if self.A_eq.size == 0:
            self.A_eq = np.empty((0, n), dtype=float)

        if self.A_ub.size == 0:
            self.A_ub = np.empty((0, n), dtype=float)

    @classmethod
    def from_json(cls, data):
        if not isinstance(data, dict):
            raise ValueError("problem must be a JSON object")

        missing = [k for k in cls.REQUIRED if k not in data]
        if missing:
            raise ValueError(f"missing required fields: {missing}")

        return cls(data)

    def validate(self):
        if self.c.ndim != 1:
            raise ValueError("c must be one-dimensional")

        n = len(self.c)

        if self.A_eq.ndim != 2:
            raise ValueError("A_eq must be two-dimensional")

        if self.A_ub.ndim != 2:
            raise ValueError("A_ub must be two-dimensional")

        if self.b_eq.ndim != 1:
            raise ValueError("b_eq must be one-dimensional")

        if self.b_ub.ndim != 1:
            raise ValueError("b_ub must be one-dimensional")

        if self.lower.ndim != 1:
            raise ValueError("lower must be one-dimensional")

        if self.upper.ndim != 1:
            raise ValueError("upper must be one-dimensional")

        if self.A_eq.shape[1] != n:
            raise ValueError(
                "A_eq column count must match c"
            )

        if self.A_ub.shape[1] != n:
            raise ValueError(
                "A_ub column count must match c"
            )

        if len(self.b_eq) != self.A_eq.shape[0]:
            raise ValueError(
                "b_eq length must match A_eq rows"
            )

        if len(self.b_ub) != self.A_ub.shape[0]:
            raise ValueError(
                "b_ub length must match A_ub rows"
            )

        if len(self.lower) != n:
            raise ValueError(
                "lower length must match c"
            )

        if len(self.upper) != n:
            raise ValueError(
                "upper length must match c"
            )

        arrays = (
            self.c,
            self.A_eq,
            self.b_eq,
            self.A_ub,
            self.b_ub,
            self.lower,
            self.upper,
        )

        for array in arrays:
            if not np.all(np.isfinite(array)):
                raise ValueError(
                    "all numerical values must be finite"
                )

        if np.any(self.lower > self.upper):
            raise ValueError(
                "lower bounds must not exceed upper bounds"
            )
