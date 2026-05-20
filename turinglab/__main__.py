"""Command line entry point for TuringLab."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from .multi_tape import MultiTapeTM
from .tm_engine import SingleTapeTM


def main() -> None:
    """Run a single-tape or multi-tape machine from a YAML file."""

    parser = argparse.ArgumentParser(description="Run a Turing machine.")
    parser.add_argument("machine", help="Path to a machine YAML file")
    parser.add_argument("input", help="Input string for the first tape")
    parser.add_argument("--max-steps", type=int, default=1000)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    machine_path = Path(args.machine)
    data = yaml.safe_load(machine_path.read_text(encoding="utf-8"))

    if isinstance(data, dict) and "num_tapes" in data:
        machine = MultiTapeTM.from_dict(data, source=str(machine_path))
    else:
        machine = SingleTapeTM.from_dict(data, source=str(machine_path))

    result = machine.run(args.input, max_steps=args.max_steps, verbose=args.verbose)
    status = "ACCEPT" if result.accepted else "REJECT"
    print(f"{status} | reason={result.reason} | steps={result.steps}")

    if hasattr(result, "final_tapes"):
        for index, tape in enumerate(result.final_tapes, start=1):
            print(f"final_tape_{index}={tape}")
    else:
        print(f"final_tape={result.final_tape}")


if __name__ == "__main__":
    main()
