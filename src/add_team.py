#!/usr/bin/env python3
"""
Script to add new sports teams to the calendar sync system.
Usage: python add_team.py "Team Name" "League" "Sport" "Calendar URL"
"""

import sys
from .team_utils import (
    clean_calendar_path,
    load_teams,
    validate_url,
    save_teams
)

def add_team(sport, league, team_name, calendar_url):
    """Add a new team to the configuration"""

    # Validate inputs
    if not all([team_name, league, sport, calendar_url]):
        print("Error: All fields are required")
        return False

    if not validate_url(calendar_url):
        print("Warning: URL doesn't appear to be a valid calendar URL")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False

    # Load existing teams
    teams_data = load_teams()

    # Generate ID
    cal_path = clean_calendar_path(sport, league, team_name)
    no_spoilers_cal_path = clean_calendar_path(sport, league, f'{team_name}_no_spoilers')


    # Check for duplicate IDs
    if cal_path in teams_data:
        print(f"Error: Team ID '{cal_path}' already exists")
        return False

    # Create new team entry
    new_team = {
        "path": cal_path,
        "sanitized_path": no_spoilers_cal_path,
        "name": team_name,
        "league": league,
        "sport": sport,
        "source_url": calendar_url
    }

    # Add to teams list
    teams_data[cal_path] = new_team

    # Save back to file
    save_teams(teams_data)

    print(f"✅ Added team: {team_name} ({league} - {sport})")
    print(f"   ID: {team_id}")
    print(f"   Calendar will be available at: calendars/{team_id}.ics")

    return True

def list_teams():
    """List all existing teams"""
    teams_data = load_teams()

    if not teams_data['teams']:
        print("No teams configured yet")
        return

    print(f"📋 {len(teams_data['teams'])} teams configured:")
    print()

    current_sport = None
    for team in teams_data['teams']:
        if team['sport'] != current_sport:
            current_sport = team['sport']
            print(f"🏈 {current_sport.upper()}")

        print(f"   {team['name']} ({team['league']}) - {team['id']}")
    print()

def main():
    if len(sys.argv) == 1:
        print("Usage: python add_team.py <command> [args]")
        print()
        print("Commands:")
        print("  add <team_name> <league> <sport> <calendar_url>")
        print("  list")
        print()
        print("Examples:")
        print('  python add_team.py add "LA Lakers" "NBA" "Basketball" "https://calendar.google.com/..."')
        print("  python add_team.py list")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "list":
        list_teams()
    elif command == "add":
        if len(sys.argv) != 6:
            print("Error: add command requires exactly 4 arguments")
            print('Usage: python add_team.py add "Team Name" "League" "Sport" "Calendar URL"')
            sys.exit(1)

        team_name = sys.argv[2]
        league = sys.argv[3]
        sport = sys.argv[4]
        calendar_url = sys.argv[5]

        if add_team(team_name, league, sport, calendar_url):
            print()
            print("Next steps:")
            print("1. git add data/teams.json")
            print(f'2. git commit -m "Add {team_name}"')
            print("3. git push")
    else:
        print(f"Unknown command: {command}")
        print("Use 'add' or 'list'")
        sys.exit(1)

if __name__ == "__main__":
    main()
