from datetime import date, datetime

import numpy as np
import pandas as pd
from diskcache import FanoutCache
from pandas import read_csv
from profilehooks import timecall

from lib.constants import UserColumns as Cols
from lib.settings import CACHE_DIR, DATA_DIR
from lib.sql import sql_to_df


@timecall
def get_users() -> pd.DataFrame:
    return _get_users_from_looker_export().pipe(_join_mixpanel_stats).pipe(
        _join_first_order_facts
    ).pipe(
        _join_pilot_users
    ).pipe(
        _join_marketing_opt_out
    ).pipe(
        _calculate_frequency_fields
    ).pipe(
        _calculate_buckets
    ).pipe(
        _cast_fields
    )


_CACHE = FanoutCache(CACHE_DIR + "looker_users", shards=1)


@_CACHE.memoize(name="4")
def _get_users_from_looker_export() -> pd.DataFrame:
    return read_csv(DATA_DIR + "customers3.csv").pipe(_rename_fields).pipe(_cast_fields)


@timecall
def _aggregate_looker_fields(users: pd.DataFrame) -> pd.DataFrame:
    # It would be ideal to detect the presence of kids and baby, but whatever.
    return users.groupby(Cols.EMAIL).max().reset_index()


_RENAME_MAP = {
    "Customer Filters Email": Cols.EMAIL,
    "Customer Segments First Order Cohort Date": Cols.FIRST_ORDER_DATE,
    "Customer Segments Lifetime Order Count": Cols.LIFETIME_ORDERS,
    "Customer Segments Lifetime GPR": Cols.LIFETIME_GPR,
    "Customer Segments Lifetime Total Units": Cols.LIFETIME_UNITS,
}


def _rename_fields(users: pd.DataFrame) -> pd.DataFrame:
    return users.rename(columns=_RENAME_MAP)

def _join_pilot_users(users: pd.DataFrame) -> pd.DataFrame:
    pilot_users = read_csv(DATA_DIR + "box_buyers.csv")
    pilot_users[Cols.EMAIL] = pilot_users[Cols.EMAIL].apply(lambda e: e.lower().strip())
    pilot_users[Cols.IS_PILOT_BOX_BUYER] = 1.0

    users = users.join(
        pilot_users.set_index(Cols.EMAIL),
        on=Cols.EMAIL,
        how="left"
    )
    users[Cols.IS_PILOT_BOX_BUYER] = users[Cols.IS_PILOT_BOX_BUYER].fillna(0.0)
    return users

def _join_marketing_opt_out(users: pd.DataFrame) -> pd.DataFrame:
    optout_users = read_csv(DATA_DIR + "marketing_opt_out.csv", names=[Cols.EMAIL])
    optout_users[Cols.EMAIL] = optout_users[Cols.EMAIL].apply(lambda e: e.lower().strip())
    optout_users[Cols.IS_MARKETING_OPT_OUT] = 1.0

    users = users.join(
        optout_users.set_index(Cols.EMAIL),
        on=Cols.EMAIL,
        how="left"
    )
    users[Cols.IS_MARKETING_OPT_OUT] = users[Cols.IS_MARKETING_OPT_OUT].fillna(0.0)
    return users


@timecall
def _cast_fields(users: pd.DataFrame) -> pd.DataFrame:
    types = Cols.types()
    for col, tipe in types.items():
        if col in users:
            if tipe == str:
                users[col] = users[col].fillna("").astype(str)
            elif tipe == float or tipe == int:
                users[col] = users[col].replace("", np.nan).replace(
                    regex=r"[$,]", value=""
                ).astype(
                    float
                )
            elif tipe == date or tipe == datetime:
                users[col] = pd.to_datetime(users[col])
    return users


def _calculate_frequency_fields(users: pd.DataFrame) -> pd.DataFrame:
    users[Cols.ORDER_FREQUENCY] = users[Cols.DAYS_RETAINED] * 1.0 / users[
        Cols.LIFETIME_ORDERS
    ]
    return users


def _calculate_buckets(users: pd.DataFrame) -> pd.DataFrame:
    users[Cols.FIRST_ORDER_MONTH] = users[Cols.FIRST_ORDER_DATE].apply(
        lambda d: datetime(d.year, d.month, 1)
    )
    users[Cols.LIFETIME_AOV] = users[Cols.LIFETIME_GPR] / users[Cols.LIFETIME_ORDERS]

    if len(users) > 10:
        users[Cols.LIFETIME_ORDERS_DECILE] = pd.qcut(
            users[Cols.LIFETIME_ORDERS], 10, labels=False, duplicates="drop"
        )

        users[Cols.LIFETIME_ORDERS_BUCKET] = pd.cut(
            users[Cols.LIFETIME_ORDERS],
            bins=[1, 2, 3, 4, 5, 6, 11, users[Cols.LIFETIME_ORDERS].max() + 1],
            labels=["1", "2", "3", "4", "5", "6-10", "11+"],
            right=False,
        )
        users[Cols.LIFETIME_AOV_BUCKET] = pd.cut(
            users[Cols.LIFETIME_AOV],
            bins=[0, 50, 101, users[Cols.LIFETIME_AOV].max() + 1],
            labels=["<50", "50-100", "100+"],
            right=False,
        )
        users[Cols.ORDERS_PER_QUARTER_BUCKET] = pd.cut(
            users[Cols.ORDERS_PER_QUARTER],
            bins=[0, 0.5, 1.0, 1.5, 2, users[Cols.ORDERS_PER_QUARTER].max() + 1],
            labels=["<0.5", "0.5", "1.0", "1.5", "2+"],
            right=False
        )

    return users


@timecall
def _join_mixpanel_stats(users: pd.DataFrame) -> pd.DataFrame:
    mixpanel_data = sql_to_df("user_visit_stats.sql").set_index(Cols.EMAIL)
    joined = users.join(mixpanel_data, on=Cols.EMAIL, how="left")
    # Single-visit users were retained for one day.
    joined[Cols.DAYS_RETAINED] = joined[Cols.DAYS_RETAINED].apply(
        lambda d: 1.0 if d < 1 else d
    )
    joined[Cols.DAYS_RETAINED_PER_VISIT] = joined[Cols.DAYS_RETAINED_PER_VISIT].apply(
        lambda d: 1.0 if d < 1 else d
    )

    joined[Cols.QUARTERS_RETAINED] = joined[Cols.DAYS_RETAINED].apply(
        lambda d: d / 90.0 if d >= 90.0 else 1.0
    )
    joined[Cols.ORDERS_PER_QUARTER] = joined[Cols.LIFETIME_ORDERS] / joined[Cols.QUARTERS_RETAINED]
    return joined


@timecall
def _join_first_order_facts(users: pd.DataFrame) -> pd.DataFrame:
    data = sql_to_df("first_order_facts.sql").set_index(Cols.EMAIL)
    data[Cols.FIRST_ORDER_DIVISION] = data[Cols.FIRST_ORDER_DIVISION].replace(
        regex=r"\|unknown", value=""
    )
    joined = users.join(data, on=Cols.EMAIL, how="left")
    return joined
