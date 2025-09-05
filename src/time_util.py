import re
from datetime import timedelta


def parse_duration(delta_str: str) -> timedelta:
    """
    Parse a string representation of a time delta into a timedelta object.

    Supported units:
    - s: seconds
    - m: minutes (lowercase)
    - mo: months (uppercase) - approximated as 30 days
    - h: hours
    - d: days
    - w: weeks
    - y: years - approximated as 365 days

    Examples:
    - "30s" -> 30 seconds
    - "5m" -> 5 minutes
    - "2mo" -> 2 months (60 days)
    - "1h" -> 1 hour
    - "7d" -> 7 days
    - "2w" -> 2 weeks
    - "1y" -> 1 year (365 days)
    - "1h30m" -> 1 hour 30 minutes
    - "2d12h30m" -> 2 days, 12 hours, 30 minutes

    Args:
        delta_str: String representation of the time delta

    Returns:
        timedelta object

    Raises:
        ValueError: If the string format is invalid
    """
    if not isinstance(delta_str, str):
        raise ValueError("Input must be a string")

    # Remove whitespace
    delta_str = delta_str.strip()

    if not delta_str:
        raise ValueError("Empty string provided")

    # Pattern to match number + unit combinations
    pattern = r'(\d+(?:\.\d+)?)\s*(mo|[smhdwy])'
    matches = re.findall(pattern, delta_str)

    if not matches:
        raise ValueError(f"No valid time units found in '{delta_str}'")

    # Check if the entire string was matched (no invalid characters)
    matched_part = ''.join(f"{num}{unit}" for num, unit in matches)
    if re.sub(r'\s+', '', delta_str) != matched_part:
        raise ValueError(f"Invalid format in '{delta_str}'. Use combinations like '1d', '2h30m', etc.")

    total_delta = timedelta()

    for value_str, unit in matches:
        value = float(value_str)

        if unit == 's':
            total_delta += timedelta(seconds=value)
        elif unit == 'm':  # minutes (lowercase)
            total_delta += timedelta(minutes=value)
        elif unit == 'mo':  # months (uppercase) - approximate as 30 days
            total_delta += timedelta(days=value * 30)
        elif unit == 'h':
            total_delta += timedelta(hours=value)
        elif unit == 'd':
            total_delta += timedelta(days=value)
        elif unit == 'w':
            total_delta += timedelta(weeks=value)
        elif unit == 'y':  # years - approximate as 365 days
            total_delta += timedelta(days=value * 365)

    return total_delta
