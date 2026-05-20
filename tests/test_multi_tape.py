from pathlib import Path

import pytest

from turinglab import MultiTapeTM


ROOT = Path(__file__).resolve().parents[1]
MACHINES = ROOT / "machines"


@pytest.mark.parametrize(
    ("input_string", "expected_reverse"),
    [
        ("", ""),
        ("0", "0"),
        ("1", "1"),
        ("101", "101"),
        ("10010", "01001"),
        ("0011", "1100"),
    ],
)
def test_binary_reverse_3tape(input_string, expected_reverse):
    tm = MultiTapeTM.from_yaml(MACHINES / "binary_reverse_3tape.yaml")

    result = tm.run(input_string, max_steps=1000)

    assert result.accepted is True
    assert result.reason == "accept"
    assert result.final_tapes[0].strip("B") == input_string
    assert result.final_tapes[1].strip("B") == input_string
    assert result.final_tapes[2].strip("B") == expected_reverse


def test_multi_tape_history_records_all_tapes():
    tm = MultiTapeTM.from_yaml(MACHINES / "binary_reverse_3tape.yaml")

    result = tm.run("10")

    assert len(result.history) == result.steps + 1
    assert len(result.history[0].tapes) == 3
    assert len(result.history[0].head_positions) == 3


def test_multi_tape_invalid_input_symbol_raises_value_error():
    tm = MultiTapeTM.from_yaml(MACHINES / "binary_reverse_3tape.yaml")

    with pytest.raises(ValueError, match="outside input_alphabet"):
        tm.run("102")


def test_multi_tape_invalid_yaml_read_length_raises_value_error(tmp_path):
    machine_file = tmp_path / "bad_multi.yaml"
    machine_file.write_text(
        """
name: bad_multi
num_tapes: 2
states: [q0, q_accept]
input_alphabet: ["0"]
tape_alphabet: ["0", "B"]
blank: "B"
start_state: q0
accept_states: [q_accept]
reject_states: []
transitions:
  - {state: q0, read: ["0"], next: q_accept, write: ["0", "B"], move: [S, S]}
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="read must be a list of length 2"):
        MultiTapeTM.from_yaml(machine_file)
