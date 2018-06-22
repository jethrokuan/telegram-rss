"""Miscellaneous utilities"""

import datetime

_DATE_FMT = "%Y%m%d%H%M%S"


def is_index(s):
    try:
        val = int(s) - 1
        return val >= 0
    except ValueError:
        return False


def now():
    return datetime.datetime.utcnow()


def date_to_string(date):
    return date.strftime(_DATE_FMT)


def string_to_date(string):
    return datetime.datetime.strptime(string, _DATE_FMT)
