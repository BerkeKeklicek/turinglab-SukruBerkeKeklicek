from pathlib import Path

import pytest

from turinglab import SingleTapeTM


ROOT = Path(__file__).resolve().parents[1]
MACHINES = ROOT / "machines"


def run_machine(file_name, input_string, max_steps=10000):
    tm = SingleTapeTM.from_yaml(MACHINES / file_name)
    return tm.run(input_string, max_steps=max_steps)


@pytest.mark.parametrize(
    ("input_string", "expected"),
    [
        ("", "0"),
        ("1", "1"),
        ("11", "10"),
        ("111", "11"),
        ("1111", "100"),
        ("11111", "101"),
    ],
)
def test_unary_to_binary(input_string, expected):
    result = run_machine("unary_to_binary.yaml", input_string)

    assert result.accepted is True
    assert result.final_tape.strip("B") == expected


@pytest.mark.parametrize(
    ("input_string", "accepted"),
    [
        ("1#0", True),
        ("10#1", True),
        ("1100#1011", True),
        ("1011#1100", False),
        ("101#101", False),
        ("0#1", False),
    ],
)
def test_binary_compare(input_string, accepted):
    result = run_machine("binary_compare.yaml", input_string)

    assert result.accepted is accepted


@pytest.mark.parametrize(
    ("input_string", "expected"),
    [
        ("", "#"),
        ("a", "a#a"),
        ("b", "b#b"),
        ("abba", "abba#abba"),
        ("baab", "baab#baab"),
    ],
)
def test_string_copy(input_string, expected):
    result = run_machine("string_copy.yaml", input_string)

    assert result.accepted is True
    assert result.final_tape.strip("B") == expected


@pytest.mark.parametrize(
    ("input_string", "accepted"),
    [
        ("0", True),
        ("100", True),
        ("1100", True),
        ("1", False),
        ("10", False),
        ("", False),
    ],
)
def test_student_choice_binary_divisible_by_4(input_string, accepted):
    result = run_machine("student_choice.yaml", input_string)

    assert result.accepted is accepted
