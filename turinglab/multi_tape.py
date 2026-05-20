"""Multi-tape deterministic Turing machine engine."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .tm_engine import Tape


@dataclass(frozen=True)
class MultiTapeConfiguration:
    """One saved configuration for a multi-tape run."""

    state: str
    tapes: list[str]
    head_positions: list[int]


@dataclass(frozen=True)
class MultiTapeRunResult:
    """Result returned by MultiTapeTM.run."""

    accepted: bool
    reason: str
    final_tapes: list[str]
    steps: int
    history: list[MultiTapeConfiguration]


@dataclass(frozen=True)
class MultiTapeTransition:
    """Internal transition record for a multi-tape machine."""

    state: str
    read: tuple[str, ...]
    next_state: str
    write: tuple[str, ...]
    move: tuple[str, ...]


class MultiTapeTM:
    """Deterministic Turing machine with k tapes."""

    def __init__(
        self,
        name: str,
        num_tapes: int,
        states: set[str],
        input_alphabet: set[str],
        tape_alphabet: set[str],
        blank: str,
        start_state: str,
        accept_states: set[str],
        reject_states: set[str],
        transitions: dict[tuple[str, tuple[str, ...]], MultiTapeTransition],
        description: str = "",
    ) -> None:
        self.name = name
        self.description = description
        self.num_tapes = num_tapes
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.blank = blank
        self.start_state = start_state
        self.accept_states = accept_states
        self.reject_states = reject_states
        self.transitions = transitions

    @classmethod
    def from_yaml(cls, path: str | Path) -> "MultiTapeTM":
        """Load a multi-tape Turing machine from YAML."""

        yaml_path = Path(path)
        try:
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML syntax in {yaml_path}: {exc}") from exc
        except OSError as exc:
            raise ValueError(f"Could not read YAML file {yaml_path}: {exc}") from exc

        return cls.from_dict(data, source=str(yaml_path))

    @classmethod
    def from_dict(cls, data: Any, source: str = "<dict>") -> "MultiTapeTM":
        """Build a machine from a parsed YAML dictionary."""

        if not isinstance(data, dict):
            raise ValueError(f"{source}: machine definition must be a mapping")

        required_fields = {
            "name",
            "num_tapes",
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

        num_tapes = _positive_int(data["num_tapes"], "num_tapes", source)
        states = _string_set(data["states"], "states", source)
        input_alphabet = _string_set(data["input_alphabet"], "input_alphabet", source)
        tape_alphabet = _string_set(data["tape_alphabet"], "tape_alphabet", source)
        accept_states = _string_set(data["accept_states"], "accept_states", source)
        reject_states = _string_set(data["reject_states"], "reject_states", source)

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

        transitions = _parse_transitions(
            data["transitions"],
            num_tapes,
            states,
            tape_alphabet,
            source,
        )

        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
            num_tapes=num_tapes,
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
        input_string: str | list[str],
        max_steps: int = 1000,
        verbose: bool = False,
    ) -> MultiTapeRunResult:
        """Run the machine with input on the first tape by default."""

        if max_steps < 0:
            raise ValueError("max_steps must be non-negative")

        input_strings = self._normalize_inputs(input_string)
        tapes = [Tape(value, self.blank) for value in input_strings]
        state = self.start_state
        steps = 0
        history = [self._configuration(state, tapes)]

        while True:
            if state in self.accept_states:
                return self._result(True, "accept", tapes, steps, history)
            if state in self.reject_states:
                return self._result(False, "reject", tapes, steps, history)
            if steps >= max_steps:
                return self._result(False, "timeout", tapes, steps, history)

            read_symbols = tuple(tape.read() for tape in tapes)
            transition = self.transitions.get((state, read_symbols))
            if transition is None:
                return self._result(False, "no_transition", tapes, steps, history)

            if verbose:
                rendered = " | ".join(tape.format_with_head() for tape in tapes)
                print(
                    f"Step {steps} | State: {state} | "
                    f"Tapes: {rendered} | Move: {list(transition.move)}"
                )

            for tape, symbol in zip(tapes, transition.write):
                tape.write(symbol)
            for tape, move in zip(tapes, transition.move):
                tape.move(move)

            state = transition.next_state
            steps += 1
            history.append(self._configuration(state, tapes))

    def _normalize_inputs(self, input_string: str | list[str]) -> list[str]:
        if isinstance(input_string, str):
            values = [input_string] + [""] * (self.num_tapes - 1)
        else:
            values = list(input_string)
            if len(values) != self.num_tapes:
                raise ValueError("input list length must match num_tapes")

        invalid_first = sorted(set(values[0]) - self.input_alphabet)
        if invalid_first:
            raise ValueError(
                "Input contains symbol(s) outside input_alphabet: "
                + ", ".join(invalid_first)
            )

        for index, value in enumerate(values[1:], start=2):
            invalid = sorted(set(value) - self.tape_alphabet)
            if invalid:
                raise ValueError(
                    f"Tape {index} contains symbol(s) outside tape_alphabet: "
                    + ", ".join(invalid)
                )

        return values

    def _configuration(
        self,
        state: str,
        tapes: list[Tape],
    ) -> MultiTapeConfiguration:
        return MultiTapeConfiguration(
            state=state,
            tapes=[tape.contents(padding=1) for tape in tapes],
            head_positions=[tape.head_position for tape in tapes],
        )

    def _result(
        self,
        accepted: bool,
        reason: str,
        tapes: list[Tape],
        steps: int,
        history: list[MultiTapeConfiguration],
    ) -> MultiTapeRunResult:
        return MultiTapeRunResult(
            accepted=accepted,
            reason=reason,
            final_tapes=[tape.contents(padding=0) for tape in tapes],
            steps=steps,
            history=history,
        )


def _positive_int(value: Any, field_name: str, source: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{source}: {field_name} must be a positive integer")
    return value


def _string_set(value: Any, field_name: str, source: str) -> set[str]:
    if not isinstance(value, list):
        raise ValueError(f"{source}: {field_name} must be a list")
    return {str(item) for item in value}


def _parse_transitions(
    raw_transitions: Any,
    num_tapes: int,
    states: set[str],
    tape_alphabet: set[str],
    source: str,
) -> dict[tuple[str, tuple[str, ...]], MultiTapeTransition]:
    if not isinstance(raw_transitions, list):
        raise ValueError(f"{source}: transitions must be a list")

    transitions: dict[tuple[str, tuple[str, ...]], MultiTapeTransition] = {}
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
        next_state = str(item["next"])
        read = _symbol_tuple(item["read"], num_tapes, "read", index, source)
        write = _symbol_tuple(item["write"], num_tapes, "write", index, source)
        move = _move_tuple(item["move"], num_tapes, index, source)

        if state not in states or next_state not in states:
            raise ValueError(f"{source}: transition #{index} references unknown state")
        if set(read) - tape_alphabet or set(write) - tape_alphabet:
            raise ValueError(f"{source}: transition #{index} uses unknown tape symbol")

        key = (state, read)
        if key in transitions:
            raise ValueError(f"{source}: duplicate transition for {state}, {read}")

        transitions[key] = MultiTapeTransition(
            state=state,
            read=read,
            next_state=next_state,
            write=write,
            move=move,
        )

    return transitions


def _symbol_tuple(
    value: Any,
    num_tapes: int,
    field_name: str,
    transition_index: int,
    source: str,
) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) != num_tapes:
        raise ValueError(
            f"{source}: transition #{transition_index} {field_name} "
            f"must be a list of length {num_tapes}"
        )
    return tuple(str(item) for item in value)


def _move_tuple(
    value: Any,
    num_tapes: int,
    transition_index: int,
    source: str,
) -> tuple[str, ...]:
    raw = _symbol_tuple(value, num_tapes, "move", transition_index, source)
    return tuple(_normalize_move(move) for move in raw)


def _normalize_move(move: str) -> str:
    if move in {"L", "R", "S"}:
        return move
    if move in {"N", "-"}:
        return "S"
    raise ValueError(f"move must be one of L, R, S, N, -; got {move}")
