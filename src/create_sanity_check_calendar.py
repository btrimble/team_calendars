import zoneinfo
from datetime import date, datetime, timedelta
from logging import warning, debug
import os

from icalendar import Calendar, cal


SANITY_CHECK_CALENDAR_PATH = 'data/sanity/calendar.ics'


def create_sanity_check_calendar():
    calendar = Calendar()
    calendar['X-WR-CALNAME'] = 'Debugging Calendar'
    calendar['PRODID'] = '-//BDOG//BDOG 1.0//EN'
    calendar['VERSION'] = '2.0'
    event = cal.Event()
    dt = date.today()
    event.start = datetime(dt.year, dt.month, dt.day, hour=18, \
        tzinfo=zoneinfo.ZoneInfo('America/Los_Angeles')) + timedelta(days=1)
    event.end = event.start + timedelta(hours=1)
    event.DTSTAMP = datetime.now()
    event.uid = '01K4Y62RYCM54BMEH8MRDQ4T1K'
    calendar.add_component(event)

    os.makedirs(os.path.dirname(SANITY_CHECK_CALENDAR_PATH), exist_ok=True)
    with open(SANITY_CHECK_CALENDAR_PATH, 'wb') as f:
        f.write(calendar.to_ical())


if __name__ == "__main__":
    create_sanity_check_calendar()
