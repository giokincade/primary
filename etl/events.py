from datetime import date
from typing import List

import pandas as pd
from profilehooks import timecall

from etl.general import coerce_types
from lib.constants import EventColumns as Cols
from lib.constants import Events
from lib.sql import sql_to_df


@timecall
def get_events(
    users: List[str], start: date = date(2018, 1, 1), end: date = date(2019, 1, 1)
) -> pd.DataFrame:
    return sql_to_df("events.sql", users=users, start=start, end=end).pipe(
        _rename_events
    ).pipe(
        coerce_types, types=Cols.types()
    )


_RENAME_MAP = {
    "Product viewed": Events.PDP,
    "products.show": Events.PDP,
    "products.index": Events.PLP,
    "home": Events.HOME,
    'viewedHomepage': Events.HOME,
    "Started Checkout Process": Events.CHECKOUT_START,
    "Checkout completed": Events.CHECKOUT,
    "Line items added": Events.BAG,
}


@timecall
def _rename_events(events: pd.DataFrame) -> pd.DataFrame:
    events[Cols.NAME] = events[Cols.NAME].replace(_RENAME_MAP)
    return events
