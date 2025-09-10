from datetime import date, datetime, timedelta
from logging import warning, debug
import os
import re
import shutil
import subprocess
import tempfile
from threading import Event
from typing import cast, Sequence

from icalendar import Calendar, cal
import requests

from team_utils import load_calendar, load_teams
from time_util import parse_duration


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


def sanitize_event(event: cal.Event):
    # Move scores from title to description
    event_keys = set(event.keys())
    if (event_keys - KNOWN_KEYS) != set():
        # TODO: Raise and catch somewhere reasonable so this doesn't short circuit the whole process
        warning(f"Unknown keys! {event_keys - KNOWN_KEYS}"); exit(1)

    for key in event_keys:
        if key in SCRUB_KEYS:
           event[key] = spoiler_free(event[key])


# returns tmp path
def fetch_calendar(team_config: dict[str, str]) -> tuple[str, str]:
    debug(f'fetching {team_config["name"]}')

    with tempfile.NamedTemporaryFile(mode='wb+', delete=False) as fcal, tempfile.NamedTemporaryFile(mode='wb+', delete=False) as fsanitized_cal:
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
        fcal.write(response.content)
        fsanitized_cal.write(response.content)

        return fcal.name, fsanitized_cal.name


def sanitize_calendar(path: str, spoiler_free_period: timedelta) -> cal.Component:
    calendar = load_calendar(path)

    events = cast(list[cal.Event], calendar.walk('vevent'))
    for event in events:
        dtstart = event.DTSTART
        if isinstance(dtstart, date):
            # Convert a date object to a datetime object (at midnight)
            dtstart = datetime(dtstart.year, dtstart.month, dtstart.day)

        if not (dtstart is None or dtstart < (datetime.now() - spoiler_free_period)):  # enough time has passed so no need to SCRUB_KEYS
            sanitize_event(event)

    with open(path, 'wb+') as f:
        f.write(calendar.to_ical(sorted=True))


def sync_calendar(team_config: dict[str, str]):
    print(team_config['path'])
    # Download source calendar
    tmp_path, sanitized_tmp_path = fetch_calendar(team_config)

    # Sanitize New Calendar
    sanitize_calendar(sanitized_tmp_path, parse_duration(team_config['spoiler_free_period']))

    # Write Calendars to Official Paths
    os.makedirs(os.path.dirname(team_config['path']), exist_ok=True)
    shutil.copy2(tmp_path, team_config['path'])
    shutil.copy2(sanitized_tmp_path, team_config['sanitized_path'])


def sync_all_calendars():
    teams = load_teams()
    for _, team in teams.items():
        sync_calendar(team)


if __name__ == "__main__":
    sync_all_calendars()
