from datetime import datetime, timedelta, date
import pytz
from dateutil.relativedelta import relativedelta
from typing import Tuple
from app.core.constants.app import DEFAULT_TZ
import arrow


def get_now() -> datetime:
    tz = pytz.timezone(DEFAULT_TZ)
    return datetime.now().replace(tzinfo=tz)

def get_age(b):
    tz = pytz.timezone(DEFAULT_TZ)
    return relativedelta(get_now(), b.replace(tzinfo=tz)).years

def get_yesterday() -> datetime:
    return get_now() - timedelta(days=1)


def get_list_week(pick_date:date) -> Tuple[datetime, datetime]:
    date_arrow = arrow.get(pick_date)
    start_date = date_arrow.floor('week')
    end_date = date_arrow.ceil('week')
    return start_date, end_date