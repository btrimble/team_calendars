import pytest
from datetime import timedelta

from time_util import parse_duration

@pytest.mark.parametrize("duration_str,expected", [
    ("30s",      timedelta(seconds=30)),
    ("5m",       timedelta(minutes=5)),
    ("2mo",      timedelta(days=60)),
    ("1h",       timedelta(hours=1)),
    ("7d",       timedelta(days=7)),
    ("2w",       timedelta(days=14)),
    ("1y",       timedelta(days=365)),
    ("1h30m",    timedelta(minutes=90)),
    ("2d12h30m", timedelta(days=2, hours=12, minutes=30)),
    ("1.5h",     timedelta(minutes=90)),
    ("0.5d",     timedelta(days=0.5)),
])
def test_cases(duration_str: str, expected: timedelta):
    assert parse_duration(duration_str) == expected


@pytest.mark.parametrize("invalid_input", [
    "",
    "abc",
    "123",
    "1x",
    "1h2x3m",
    "1z",           # Invalid unit
    "1h2z3m",       # Invalid unit in middle
    "h",            # Missing number
    "1.h",          # Invalid decimal
    "1..5h",        # Double decimal
    "1h2",          # Missing unit at end
    "",             # Empty string
    "   ",          # Whitespace only
])
def test_error_cases(invalid_input: str):
    with pytest.raises(ValueError):
        parse_duration(invalid_input)
