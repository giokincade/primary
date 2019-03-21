from datetime import date
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from lib.constants import TransactionColumns, UserColumns
from lib.sql import sql_to_df
from lib.viz import Colors, init_plt


def orders_per_year(users: pd.DataFrame):
    init_plt()
    sns.distplot(
        users[UserColumns.ORDERS_PER_YEAR],
        kde=False
    )
    plt.gcf().suptitle("Orders per Year")
    plt.xlim(0, 10)
    plt.ylabel("Users")
    plt.xlabel("Orders per Year")
    plt.show()
    display(users[UserColumns.ORDERS_PER_YEAR].describe(
        percentiles=[.1, .2, .3, .4, .5, .6, .7, .8, .9, .95]
    ))


def subscription_op_size(
    users: pd.DataFrame,
    margin: 0.65,
    shipping: 6.0
):
    sorted = users.sort_values(UserColumns.ORDERS_PER_YEAR, ascending=False)[[
        UserColumns.ORDERS_PER_YEAR,
        UserColumns.LIFETIME_AOV
    ]].copy()

    def new_subscription_orders(orders_per_year: int):
        return max(0 , 4.0 - math.floor(orders_per_year))

    sorted["new_orders"] = sorted["orders_per_year"].apply(new_orders)
    sorted["new_revenue"] = sorted["new_orders"] * 68
    sorted["cumulative_new_revenue"] = sorted["new_revenue"].cumsum()

    display(np.percentile(sorted["cumulative_new_revenue"], [10, 20, 3]))
    percents = list(range(1,101))
    opp_size = pd.DataFrame({
        "coverage_percentage": percents,
        "new_yearly_revenue": np.percentile(sorted["cumulative_new_revenue"], percents)
    })
    display(opp_size)
