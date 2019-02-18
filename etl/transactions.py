import math
from datetime import date

import pandas as pd
from profilehooks import timecall

from etl.general import coerce_types
from lib.constants import TransactionColumns as Cols
from lib.sql import sql_to_df


@timecall
def get_transactions() -> pd.DataFrame:
    return sql_to_df("transactions.sql").pipe(coerce_types, types=Cols.types()).pipe(
        _calculate_fields
    )


def _calculate_fields(transactions: pd.DataFrame) -> pd.DataFrame:
    transactions[Cols.COMMON_PRODUCTS_RATIO] = transactions[
        Cols.COMMON_PRODUCTS
    ] / transactions[
        Cols.PRODUCTS
    ] * 100.0
    transactions[Cols.COMMON_UNITS_RATIO] = transactions[
        Cols.COMMON_UNITS
    ] / transactions[
        Cols.UNITS
    ] * 100.0
    transactions[Cols.COMMON_TOTAL_RATIO] = transactions[
        Cols.COMMON_TOTAL
    ] / transactions[
        Cols.ITEM_TOTAL
    ] * 100.0
    transactions[Cols.ORDER_INDEX_BUCKET] = pd.cut(
        transactions[Cols.ORDER_INDEX],
        bins=[2, 3, 4, 5, 100],
        labels=["2", "3", "4", "5+"],
        right=False,
        include_lowest=True,
    )
    transactions[Cols.IS_REPEAT] = (transactions[Cols.ORDER_INDEX] > 1.0).astype(float)
    transactions[Cols.DISCOUNT_PERCENTAGE] = transactions[Cols.ADJUSTMENT_TOTAL].apply(
        lambda a: 0.0 if a > 0.0 else math.fabs(a)
    ) / transactions[
        Cols.ITEM_TOTAL
    ] * 100.0
    transactions[Cols.ORDER_DATE] = transactions[Cols.ORDER_COMPLETED_AT].apply(
        lambda d: d.date()
    )
    transactions[Cols.ORDER_MONTH] = transactions[Cols.ORDER_COMPLETED_AT].apply(
        lambda d: date(d.year, d.month, 1)
    )
    return transactions
