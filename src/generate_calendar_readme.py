from team_utils import load_teams


TEAM_CALENDAR_README_PREFIX = \
"""
# Team Calendars

Hi! Please pick a calendar link from the list below:

| Sport | League | Team | Google Calendar Links |
| ------ | -------- | ------- | ----- |
"""

TABLE_ROW_TEMPLATE = \
    "| {sport} | {league} | {team} | ( [Standard]({link}) \\| [No Spoilers]({spoiler_free_link}) ) |\n"
LINK_TEMPLATE = "https://raw.githubusercontent.com/btrimble/team_calendars/refs/heads/main/{path}"

def create_readme():
    teams = load_teams()
    with open("calendars.md", "w") as f:
        f.write(TEAM_CALENDAR_README_PREFIX)
        for _, team in teams.items():
            link = LINK_TEMPLATE.format(path=team['path'])
            spoiler_free_link = LINK_TEMPLATE.format(path=team['sanitized_path'])
            row = TABLE_ROW_TEMPLATE.format(
                sport=team["sport"],
                league=team["league"],
                team=team["name"],
                link=link,
                spoiler_free_link=spoiler_free_link,
            )
            f.write(row)


if __name__ == "__main__":
    create_readme()
