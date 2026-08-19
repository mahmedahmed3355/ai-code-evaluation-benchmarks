from dataclasses import dataclass


@dataclass
class ValidationMetrics:
    total: int = 0
    passed: int = 0
    failed: int = 0

    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0

        return self.passed / self.total

    def record_success(self) -> None:
        self.total += 1
        self.passed += 1

    def record_failure(self) -> None:
        self.total += 1
        self.failed += 1

    def to_dict(self) -> dict[str, int | float]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "success_rate": self.success_rate,
        }
