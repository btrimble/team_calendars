from logging import warning, debug
import os
import re
import shutil
import subprocess
import tempfile
from threading import Event
from typing import cast

from icalendar import Calendar, cal
import requests

from team_utils import load_calendar, load_teams


KNOWN_KEYS = {
    'CLASS',
    'DESCRIPTION',
    'DTSTAMP',
    'DTSTART',
    'DTEND',
    'LAST-MODIFIED',
    'LOCATION',
    'PRIORITY',
    'SEQUENCE',
    'STATUS',
    'SUMMARY',
    'TRANSP',
    'UID',
    'URL',
}

SCRUB_KEYS = {
    'DESCRIPTION',
    'SUMMARY',
}

UNIQUE_ID = "UID"

# Detect score patterns (common formats). Should I change this to just not modify existing entries?
SCRUB_PATTERNS = [
    r'\d+-\d+',  # "3-1"
    r'\(\d+-\d+\)',  # "(3-1)"
    r'[Ww]in|[Ll]oss|[Tt]ie',  # Win/Loss indicators
]


def spoiler_free(s: str) -> str:
    clean_s = s
    for pattern in SCRUB_PATTERNS:
        clean_s = re.sub(pattern, '', clean_s).strip()
    return clean_s


def sanitize_event(event: cal.Event) -> cal.Event:
    # Move scores from title to description
    event_keys = set(event.keys())
    if (event_keys - KNOWN_KEYS) != set():
        # TODO: Raise and catch somewhere reasonable so this doesn't short circuit the whole process
        warning(f"Unknown keys! {event_keys - KNOWN_KEYS}"); exit(1)

    sanitized_event = cal.Event()
    for key in event_keys:
        if key in SCRUB_KEYS:
           sanitized_event[key] = spoiler_free(event[key])
        else:
            sanitized_event[key] = event[key]

    return sanitized_event


# returns tmp path
def fetch_calendar(team_config: dict[str, str]) -> str:
    debug(f'fetching {team_config["name"]}')

    with tempfile.NamedTemporaryFile(mode='wb+', delete=False) as named_tmp_file:
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
                'Accept': 'application/json',
                # Add other headers as needed
        }
        response = requests.get(
            team_config['source_url'],
            headers=headers,
            allow_redirects=True
        )  # type: requests.Response
        named_tmp_file.write(response.content)
        return named_tmp_file.name


def sha256_file(path: str) -> str:
    if not os.path.exists(path):
        return ""
    result = subprocess.run(["sha256", "-q", path], capture_output=True, text=True, check=True)
    return result.stdout


def sanitize_calendar(path) -> cal.Component:
    cal = load_calendar(path)
    sanitized_cal = Calendar()
    for event in cal.walk('vevent'):
        sanitized_cal.add_component(sanitize_event(event))

    return sanitized_cal


def sync_calendar(team_config: dict[str, str]):
    # Download source calendar
    tmp_path = fetch_calendar(team_config)

    # Compare Calendar Files
    if sha256_file(tmp_path) == sha256_file(team_config['path']):
        debug(f"Skipping {team_config['path']}")
        return

    # Sanitize New Calendar
    cal = sanitize_calendar(tmp_path)

    # Write Calendars to Official Paths
    os.makedirs(os.path.dirname(team_config['path']), exist_ok=True)
    shutil.copy2(tmp_path, team_config['path'])
    with open(team_config['sanitized_path'], 'wb+') as f:
        f.write(cal.to_ical(sorted=True))


def sync_all_calendars():
    teams = load_teams()
    for _, team in teams.items():
        sync_calendar(team)


if __name__ == "__main__":
    sync_all_calendars()
