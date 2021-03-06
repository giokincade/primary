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
        _join_user_list,
        file="primary_picks_pilot_buyers.csv",
        column=Cols.IS_PICKS_BUYER
    ).pipe(
        _join_user_list,
        file="primary_picks_waitlist.csv",
        column=Cols.IS_PICKS_WAITLIST
    ).pipe(
        _join_user_list,
        file="marketing_opt_out.csv",
        column=Cols.IS_MARKETING_OPT_OUT
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

@timecall
def _join_user_list(
    users: pd.DataFrame,
    file="box_buyers.csv",
    column=Cols.IS_PICKS_BUYER
) -> pd.DataFrame:
    """
    Denote the presence of each user in `file` with an indicator in `column`.
    """
    user_list = read_csv(DATA_DIR + file)
    user_list[Cols.EMAIL] = user_list[Cols.EMAIL].apply(lambda e: e.lower().strip())
    user_list[column] = 1.0

    users = users.join(
        user_list.set_index(Cols.EMAIL),
        on=Cols.EMAIL,
        how="left"
    )
    users[column] = users[column].fillna(0.0)
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

    joined[Cols.YEARS_RETAINED] = joined[Cols.DAYS_RETAINED].apply(
        lambda d: d / 365.0 if d >= 365.0 else 1.0
    )
    joined[Cols.ORDERS_PER_YEAR] = joined[Cols.LIFETIME_ORDERS] / joined[Cols.YEARS_RETAINED]
    return joined


@timecall
def _join_first_order_facts(users: pd.DataFrame) -> pd.DataFrame:
    data = sql_to_df("first_order_facts.sql").set_index(Cols.EMAIL)
    data[Cols.FIRST_ORDER_DIVISION] = data[Cols.FIRST_ORDER_DIVISION].replace(
        regex=r"\|unknown", value=""
    )
    data[Cols.FIRST_ORDER_HAS_BABY] = data[Cols.FIRST_ORDER_DIVISION].isin(["baby", "baby|kids"]).astype(int).astype(float) * 1.0
    data[Cols.FIRST_ORDER_HAS_KIDS] = data[Cols.FIRST_ORDER_DIVISION].isin(["kids", "baby|kids"]).astype(int).astype(float) * 1.0
    joined = users.join(data, on=Cols.EMAIL, how="left")
    return joined
