from pathlib import Path

import pytest

from turinglab import SingleTapeTM


ROOT = Path(__file__).resolve().parents[1]
MACHINES = ROOT / "machines"


@pytest.mark.parametrize(
    ("input_string", "expected"),
    [
        ("0", "1"),
        ("1", "10"),
        ("10", "11"),
        ("11", "100"),
        ("1011", "1100"),
    ],
)
def test_binary_increment_outputs_expected_value(input_string, expected):
    tm = SingleTapeTM.from_yaml(MACHINES / "binary_increment.yaml")

    result = tm.run(input_string, max_steps=1000)

    assert result.accepted is True
    assert result.reason == "accept"
    assert result.final_tape.strip("B") == expected


@pytest.mark.parametrize(
    ("input_string", "expected"),
    [
        ("", "1"),
        ("1", "11"),
        ("11", "111"),
        ("111", "1111"),
        ("1111", "11111"),
    ],
)
def test_unary_increment_outputs_expected_value(input_string, expected):
    tm = SingleTapeTM.from_yaml(MACHINES / "unary_increment.yaml")

    result = tm.run(input_string)

    assert result.accepted is True
    assert result.final_tape.strip("B") == expected


@pytest.mark.parametrize(
    ("input_string", "accepted"),
    [
        ("", True),
        ("a", False),
        ("aa", True),
        ("aaa", False),
        ("aaaa", True),
    ],
)
def test_even_a_accepts_only_even_lengths(input_string, accepted):
    tm = SingleTapeTM.from_yaml(MACHINES / "even_a.yaml")

    result = tm.run(input_string)

    assert result.accepted is accepted


def test_history_contains_initial_configuration_and_each_step():
    tm = SingleTapeTM.from_yaml(MACHINES / "binary_increment.yaml")

    result = tm.run("1011")

    assert len(result.history) == result.steps + 1
    assert result.history[0].state == "q0"
    assert result.history[-1].state == "q_accept"


def test_no_transition_result(tmp_path):
    machine_file = tmp_path / "no_transition.yaml"
    machine_file.write_text(
        """
name: no_transition
states: [q0, q_accept]
input_alphabet: ["0"]
tape_alphabet: ["0", "B"]
blank: "B"
start_state: q0
accept_states: [q_accept]
reject_states: []
transitions: []
""".strip(),
        encoding="utf-8",
    )
    tm = SingleTapeTM.from_yaml(machine_file)

    result = tm.run("0")

    assert result.accepted is False
    assert result.reason == "no_transition"


def test_timeout_result(tmp_path):
    machine_file = tmp_path / "timeout.yaml"
    machine_file.write_text(
        """
name: timeout
states: [q0]
input_alphabet: []
tape_alphabet: ["B"]
blank: "B"
start_state: q0
accept_states: []
reject_states: []
transitions:
  - {state: q0, read: "B", next: q0, write: "B", move: S}
""".strip(),
        encoding="utf-8",
    )
    tm = SingleTapeTM.from_yaml(machine_file)

    result = tm.run("", max_steps=3)

    assert result.accepted is False
    assert result.reason == "timeout"
    assert result.steps == 3


def test_invalid_yaml_raises_value_error(tmp_path):
    machine_file = tmp_path / "bad.yaml"
    machine_file.write_text("name: bad\nstates: [q0]\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required"):
        SingleTapeTM.from_yaml(machine_file)


def test_verbose_output_marks_head_position(capsys):
    tm = SingleTapeTM.from_yaml(MACHINES / "binary_increment.yaml")

    tm.run("1", max_steps=10, verbose=True)
    output = capsys.readouterr().out

    assert "Adım 0" in output
    assert "Durum: q0" in output
    assert "[1]B" in output


def test_reject_state_returns_reject_reason():
    tm = SingleTapeTM.from_yaml(MACHINES / "even_a.yaml")

    result = tm.run("a")

    assert result.accepted is False
    assert result.reason == "reject"
