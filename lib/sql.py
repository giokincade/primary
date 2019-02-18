import os

import pandas as pd
import snowflake.connector
from diskcache import FanoutCache
from profilehooks import timecall

from lib.settings import (
    CACHE_DIR,
    SNOWFLAKE_ACCOUNT,
    SNOWFLAKE_DATABASE,
    SNOWFLAKE_PASSWORD,
    SNOWFLAKE_USER,
    SNOWFLAKE_WAREHOUSE,
    SQL_DIR,
)


@timecall
def sql_to_df(sql: str, use_cache=True, **kwargs) -> pd.DataFrame:
    # Check if the argument is a SQL file
    possible_files = [sql, SQL_DIR + sql]
    for file_path in possible_files:
        if os.path.isfile(file_path):
            with open(file_path) as file:
                sql = file.read()
    if use_cache:
        return _cached_sql_to_df(sql, **kwargs)

    else:
        return _cached_sql_to_df.__wrapped__(sql, **kwargs)


_CACHE = FanoutCache(CACHE_DIR + "sql", shards=1)


@_CACHE.memoize(name="1")
def _cached_sql_to_df(sql: str, **kwargs) -> pd.DataFrame:
    with _get_conneciton() as conn:
        with conn.cursor() as curr:
            curr = curr.execute(sql, kwargs)
            results = curr.fetchall()
            cols = [c[0].lower() for c in curr.description]
            return pd.DataFrame(results, columns=cols)


def _get_conneciton():
    return snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        database=SNOWFLAKE_DATABASE,
        warehouse=SNOWFLAKE_WAREHOUSE,
    )
