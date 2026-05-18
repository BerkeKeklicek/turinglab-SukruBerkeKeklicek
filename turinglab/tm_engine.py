"""Single-tape deterministic Turing machine engine."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Configuration:
    """One saved machine configuration in a run history."""

    state: str
    tape: str
    head_position: int


@dataclass(frozen=True)
class RunResult:
    """Result object returned by SingleTapeTM.run."""

    accepted: bool
    reason: str
    final_tape: str
    steps: int
    history: list[Configuration]


@dataclass(frozen=True)
class Transition:
    """Internal representation of one delta rule."""

    state: str
    read: str
    next_state: str
    write: str
    move: str


class Tape:
    """Sparse infinite tape for a single-tape Turing machine."""

    def __init__(self, input_string: str = "", blank: str = "B") -> None:
        self.blank = blank
        self.head_position = 0
        self._cells: dict[int, str] = {
            index: symbol for index, symbol in enumerate(input_string)
        }

    def read(self) -> str:
        """Return the symbol under the current head."""

        return self._cells.get(self.head_position, self.blank)

    def write(self, symbol: str) -> None:
        """Write a symbol to the current head location."""

        if symbol == self.blank:
            self._cells.pop(self.head_position, None)
        else:
            self._cells[self.head_position] = symbol

    def move(self, direction: str) -> None:
        """Move the head left, right, or stay in place."""

        if direction == "L":
            self.head_position -= 1
        elif direction == "R":
            self.head_position += 1
        elif direction == "S":
            return
        else:
            raise ValueError(f"Unknown move direction: {direction}")

    def contents(self, padding: int = 0) -> str:
        """Return tape contents from the leftmost used cell to the rightmost one."""

        start, end = self._visible_bounds(padding)
        return "".join(self._cells.get(i, self.blank) for i in range(start, end + 1))

    def format_with_head(self, padding: int = 1) -> str:
        """Return a tape string where the current head cell is shown in brackets."""

        start, end = self._visible_bounds(padding)
        parts: list[str] = []
        for position in range(start, end + 1):
            symbol = self._cells.get(position, self.blank)
            if position == self.head_position:
                parts.append(f"[{symbol}]")
            else:
                parts.append(symbol)
        return "".join(parts)

    def _visible_bounds(self, padding: int) -> tuple[int, int]:
        used_positions = set(self._cells) or {0}
        start = min(min(used_positions), self.head_position, 0)
        end = max(max(used_positions) + padding, self.head_position, 0)
        return start, end


class SingleTapeTM:
    """Deterministic single-tape Turing machine loaded from YAML."""

    def __init__(
        self,
        name: str,
        states: set[str],
        input_alphabet: set[str],
        tape_alphabet: set[str],
        blank: str,
        start_state: str,
        accept_states: set[str],
        reject_states: set[str],
        transitions: dict[tuple[str, str], Transition],
        description: str = "",
    ) -> None:
        self.name = name
        self.description = description
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.blank = blank
        self.start_state = start_state
        self.accept_states = accept_states
        self.reject_states = reject_states
        self.transitions = transitions

    @classmethod
    def from_yaml(cls, path: str | Path) -> "SingleTapeTM":
        """Load a Turing machine definition from a YAML file."""

        yaml_path = Path(path)
        try:
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML syntax in {yaml_path}: {exc}") from exc
        except OSError as exc:
            raise ValueError(f"Could not read YAML file {yaml_path}: {exc}") from exc

        return cls.from_dict(data, source=str(yaml_path))

    @classmethod
    def from_dict(cls, data: Any, source: str = "<dict>") -> "SingleTapeTM":
        """Build a machine from a parsed YAML dictionary."""

        if not isinstance(data, dict):
            raise ValueError(f"{source}: machine definition must be a mapping")

        required_fields = {
            "name",
            "states",
            "input_alphabet",
            "tape_alphabet",
            "blank",
            "start_state",
            "accept_states",
            "reject_states",
            "transitions",
        }
        missing = sorted(required_fields - set(data))
        if missing:
            raise ValueError(f"{source}: missing required field(s): {', '.join(missing)}")

        states = _string_set(data["states"], "states", source)
        input_alphabet = _string_set(data["input_alphabet"], "input_alphabet", source)
        tape_alphabet = _string_set(data["tape_alphabet"], "tape_alphabet", source)
        accept_states = _string_set(data["accept_states"], "accept_states", source)
        reject_states = _string_set(data["reject_states"], "reject_states", source)

        name = str(data["name"])
        description = str(data.get("description", ""))
        blank = str(data["blank"])
        start_state = str(data["start_state"])

        if blank not in tape_alphabet:
            raise ValueError(f"{source}: blank symbol must be in tape_alphabet")
        if not input_alphabet <= tape_alphabet:
            raise ValueError(f"{source}: input_alphabet must be subset of tape_alphabet")
        if start_state not in states:
            raise ValueError(f"{source}: start_state is not listed in states")
        if not accept_states <= states:
            raise ValueError(f"{source}: accept_states contains unknown state")
        if not reject_states <= states:
            raise ValueError(f"{source}: reject_states contains unknown state")

        transitions = _parse_transitions(data["transitions"], states, tape_alphabet, source)

        return cls(
            name=name,
            description=description,
            states=states,
            input_alphabet=input_alphabet,
            tape_alphabet=tape_alphabet,
            blank=blank,
            start_state=start_state,
            accept_states=accept_states,
            reject_states=reject_states,
            transitions=transitions,
        )

    def run(
        self,
        input_string: str,
        max_steps: int = 1000,
        verbose: bool = False,
    ) -> RunResult:
        """Run the machine on input_string and return a RunResult."""

        if max_steps < 0:
            raise ValueError("max_steps must be non-negative")
        self._validate_input(input_string)

        tape = Tape(input_string=input_string, blank=self.blank)
        state = self.start_state
        steps = 0
        history = [self._configuration(state, tape)]

        while True:
            if state in self.accept_states:
                return self._result(True, "accept", tape, steps, history)
            if state in self.reject_states:
                return self._result(False, "reject", tape, steps, history)
            if steps >= max_steps:
                return self._result(False, "timeout", tape, steps, history)

            read_symbol = tape.read()
            transition = self.transitions.get((state, read_symbol))
            if transition is None:
                return self._result(False, "no_transition", tape, steps, history)

            if verbose:
                print(
                    f"Adım {steps} | Durum: {state} | "
                    f"Şerit: {tape.format_with_head()} | Hareket: {transition.move}"
                )

            tape.write(transition.write)
            tape.move(transition.move)
            state = transition.next_state
            steps += 1
            history.append(self._configuration(state, tape))

    def _validate_input(self, input_string: str) -> None:
        invalid = sorted(set(input_string) - self.input_alphabet)
        if invalid:
            raise ValueError(
                "Input contains symbol(s) outside input_alphabet: "
                + ", ".join(invalid)
            )

    def _configuration(self, state: str, tape: Tape) -> Configuration:
        return Configuration(
            state=state,
            tape=tape.contents(padding=1),
            head_position=tape.head_position,
        )

    def _result(
        self,
        accepted: bool,
        reason: str,
        tape: Tape,
        steps: int,
        history: list[Configuration],
    ) -> RunResult:
        return RunResult(
            accepted=accepted,
            reason=reason,
            final_tape=tape.contents(padding=0),
            steps=steps,
            history=history,
        )


TuringMachine = SingleTapeTM


def _string_set(value: Any, field_name: str, source: str) -> set[str]:
    if not isinstance(value, list):
        raise ValueError(f"{source}: {field_name} must be a list")
    return {str(item) for item in value}


def _parse_transitions(
    raw_transitions: Any,
    states: set[str],
    tape_alphabet: set[str],
    source: str,
) -> dict[tuple[str, str], Transition]:
    if not isinstance(raw_transitions, list):
        raise ValueError(f"{source}: transitions must be a list")

    transitions: dict[tuple[str, str], Transition] = {}
    for index, item in enumerate(raw_transitions, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{source}: transition #{index} must be a mapping")

        missing = {"state", "read", "next", "write", "move"} - set(item)
        if missing:
            raise ValueError(
                f"{source}: transition #{index} missing field(s): "
                + ", ".join(sorted(missing))
            )

        state = str(item["state"])
        read = str(item["read"])
        next_state = str(item["next"])
        write = str(item["write"])
        move = _normalize_move(str(item["move"]))

        if state not in states or next_state not in states:
            raise ValueError(f"{source}: transition #{index} references unknown state")
        if read not in tape_alphabet or write not in tape_alphabet:
            raise ValueError(f"{source}: transition #{index} uses unknown tape symbol")

        key = (state, read)
        if key in transitions:
            raise ValueError(
                f"{source}: duplicate transition for state={state}, read={read}"
            )

        transitions[key] = Transition(
            state=state,
            read=read,
            next_state=next_state,
            write=write,
            move=move,
        )

    return transitions


def _normalize_move(move: str) -> str:
    if move in {"L", "R", "S"}:
        return move
    if move in {"N", "-"}:
        return "S"
    raise ValueError(f"move must be one of L, R, S, N, -; got {move}")


def main() -> None:
    """Small command line interface for manual demos."""

    import argparse

    parser = argparse.ArgumentParser(description="Run a single-tape Turing machine.")
    parser.add_argument("machine", help="Path to a machine YAML file")
    parser.add_argument("input", help="Input string for the machine")
    parser.add_argument("--max-steps", type=int, default=1000)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    tm = SingleTapeTM.from_yaml(args.machine)
    result = tm.run(args.input, max_steps=args.max_steps, verbose=args.verbose)
    status = "ACCEPT" if result.accepted else "REJECT"
    print(f"{status} | reason={result.reason} | steps={result.steps}")
    print(f"final_tape={result.final_tape}")


if __name__ == "__main__":
    main()
