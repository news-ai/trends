# Stdlib imports
import datetime

# Third-party app imports
import dateutil.parser as parser
from pattern.db import date as dbdate
from pattern.web import plaintext


def datetext(date, description):
    dt = parser.parse(date)
    dt = dt.strftime("%Y-%m-%d")
    d = str(dbdate(dt, format='%Y-%m-%d'))
    s = plaintext(description)
    return (d, s)


def timestamptext(date, story):
    dt = datetime.datetime.fromtimestamp(
        story['added_at']).strftime('%Y-%m-%d')
    dt = parser.parse(dt)
    dt = dt.strftime("%Y-%m-%d")
    d = str(dbdate(dt, format='%Y-%m-%d'))
    s = plaintext(description)
    return (d, s)
