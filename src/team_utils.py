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
    sport, league, name = (re.sub(r'^\w\s-_', '', x) for x in (sport, league, name))
    path = os.path.join(sport, league, name).lower()
    path = path + '.ics'
    return re.sub(r'[-\s]+', '_', path)


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
