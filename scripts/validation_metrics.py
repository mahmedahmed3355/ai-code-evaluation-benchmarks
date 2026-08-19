from dataclasses import asdict, dataclass


@dataclass
class ValidationMetrics:
    total_tasks: int = 0
    passed_tasks: int = 0
    failed_tasks: int = 0

    @property
    def success_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0

        return round((self.passed_tasks / self.total_tasks) * 100, 2)

    def to_dict(self) -> dict[str, int | float]:
        data = asdict(self)
        data["success_rate"] = self.success_rate
        return data
