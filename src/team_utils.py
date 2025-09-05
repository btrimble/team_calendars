#!/usr/bin/env python3
"""
Helper functions for managing the team configuration file
"""
import json
import os
import sys
import re

from icalendar import Calendar, cal


def teams_file_path() -> str:
    return os.path.join('data', 'teams.json')


def clean_calendar_path(sport: str, league: str, name: str):
    """Generate a clean ID from team name and league"""

    path = os.path.join(sport, league, name)

    # Convert to lowercase, remove special chars, replace spaces with underscores
    clean_id = re.sub(r'[^\w\s-]', '', path.lower())
    clean_id = re.sub(r'[-\s]+', '_', clean_id)
    return clean_id.strip('-')


def load_teams() -> dict[str, dict[str, str]]:
    """Load existing teams from teams.json"""
    teams_file = teams_file_path()

    with open(teams_file, 'r') as f:
        return json.load(f)


def load_calendar(path) -> cal.Component:
    with open(path, 'r') as f:
        return Calendar.from_ical(f.read())


def save_teams(teams_data: dict):
    """Save teams data back to teams.json"""
    with open(teams_file_path(), 'w') as f:
        json.dump(teams_data, f, indent=2, sort_keys=True)

# this seems kinda dumb -- it might make more sense to run the sync when CRUDing a team instead.
def validate_url(url: str) -> bool:
    """Basic validation for calendar URL"""
    if not url.startswith(('http://', 'https://')):
        return False
    # Check for common calendar URL patterns
    calendar_patterns = [
        'calendar.google.com',
        'outlook.live.com',
        'calendar.yahoo.com',
        '.ics'
    ]
    return any(pattern in url for pattern in calendar_patterns)
