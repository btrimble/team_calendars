#!/usr/bin/env python3
"""
Script to add new sports teams to the calendar sync system.
Usage: python add_team.py "Team Name" "League" "Sport" "Calendar URL"
"""

import sys
from team_utils import (
    clean_calendar_path,
    load_teams,
    save_teams
)


"""
"league": "La Liga",
"name": "Real Madrid",
"path": "data/soccer/laliga/real_madrid.ics",
"sanitized_path": "data/soccer/laliga/no_spoilers_real_madrid.ics",
"source_url": "https://pub.fotmob.com/prod/pub/api/v2/calendar/team/8633.ics",
"spoiler_free_period": "7d",
"sport": "Soccer"
"""


def upsert_team(sport: str, league: str, team_name: str, calendar_url: str, spoiler_free_period: str="365d"):
    """Add a new team to the configuration"""
    # Load existing teams
    teams_data = load_teams()

    # Generate paths
    cal_path = clean_calendar_path(sport, league, team_name)
    no_spoilers_cal_path = clean_calendar_path(sport, league, f'{team_name}_no_spoilers')

    # Check for duplicate IDs
    if cal_path in teams_data:
        print(f"UPDATING '{cal_path}'")
    else:
        print(f"ADDING '{cal_path}'")


    # Create new team entry
    new_team = {
        "league": league,
        "name": team_name,
        "path": cal_path,
        "sanitized_path": no_spoilers_cal_path,
        "source_url": calendar_url,
        "spoiler_free_period": spoiler_free_period,
        "sport": sport,
    }

    # Add to teams list
    teams_data[cal_path] = new_team

    # Save back to file
    save_teams(teams_data)

    print(f"✅ Added team: {team_name} ({league} - {sport})")
    print(f"   Calendar will be available at: {cal_path}")
    print(f"                             and: {no_spoilers_cal_path}")

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
    for _, team in teams_data.items():
        if team['sport'] != current_sport:
            current_sport = team['sport']
            print(f"🏈 {current_sport.upper()}")

        print(f"   {team['sport']} {team['league']} {team['name']}")
    print()


def print_usage():
    print("Usage: python upsert_team.py <command> [args]")
    print()
    print("Commands:")
    print("  upsert <sport> <league> <name> <ics url> [spoiler_free_period]")
    print("  list")
    print()
    print("Examples:")
    print('  python upsert_team.py add "Basketball" "NBA" "LA Lakers" "https://calendar.google.com/..."')
    print("  python upsert_team.py list")


# TODO: Modify this to use some kind of arg parsing library
def main():
    argc = len(sys.argv)
    if argc == 1:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "list":
        list_teams()
    elif command == "upsert":
        if argc != 6 and argc != 7:
            print("Error: add command requires 4 or 5 arguments")
            print_usage()
            sys.exit(1)

        sport = sys.argv[2]
        league = sys.argv[3]
        team_name = sys.argv[4]
        calendar_url = sys.argv[5]
        spoiler_free_period = "365d"
        if argc == 7:
            spoiler_free_period = sys.argv[6]

        if upsert_team(sport, league, team_name, calendar_url, spoiler_free_period):
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
