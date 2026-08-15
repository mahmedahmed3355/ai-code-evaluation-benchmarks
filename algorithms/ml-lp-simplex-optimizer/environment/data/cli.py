import argparse
import json

from optimizer import solve
from problem import LPProblem


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("problem")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.problem, "r", encoding="utf-8") as f:
        data = json.load(f)

    problem = LPProblem.from_json(data)
    result = solve(problem)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
