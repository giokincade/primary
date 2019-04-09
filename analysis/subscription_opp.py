from datetime import date
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from lib.constants import TransactionColumns, UserColumns
from lib.sql import sql_to_df
from lib.viz import Colors, init_plt


ASSUMED_BOX_PROFIT = 23.10

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
    margin=0.65,
    shipping= 6.0
):
    init_plt()
    sorted = users.sort_values(UserColumns.ORDERS_PER_YEAR, ascending=False)[[
        UserColumns.ORDERS_PER_YEAR,
        UserColumns.LIFETIME_AOV
    ]].copy()
    sorted["one"] = 1.0

    def new_subscription_orders(orders_per_year: int):
        return max(0 , 4.0 - math.floor(orders_per_year))

    sorted["new_orders"] = sorted["orders_per_year"].apply(new_subscription_orders)
    sorted["new_revenue"] = sorted["new_orders"] * 68
    sorted["new_profit"] = sorted["new_orders"] * 23.10
    sorted["cumulative_new_revenue"] = sorted["new_revenue"].cumsum()
    sorted["cumulative_new_profit"] = sorted["new_profit"].cumsum()
    sorted["cumulative_users"] = sorted["one"].cumsum()

    sns.lineplot(
        x="cumulative_users",
        y="cumulative_new_revenue",
        data=sorted
    )
    plt.xlim(0, 50000)
    plt.ylim(0, 2000000)
    plt.gcf().suptitle("Additional Yearly Revenue based on Subscription Users")
    plt.xlabel("Subscription Users")
    plt.ylabel("Additional Yearly Revenue")
    plt.show()

    sns.lineplot(
        x="cumulative_users",
        y="cumulative_new_profit",
        data=sorted
    )
    plt.xlim(0, 50000)
    plt.ylim(0, 600000)
    plt.gcf().suptitle("Additional Yearly Profit based on Subscription Users")
    plt.xlabel("Subscription Users")
    plt.ylabel("Additional Yearly Profit")
    plt.show()


    percents = list(range(1,51))
    opp_size = pd.DataFrame({
        "coverage_percentage": percents,
        "cumulative_new_revenue": np.percentile(sorted["cumulative_new_revenue"], percents),
        "cumulative_new_profit": np.percentile(sorted["cumulative_new_profit"], percents),
        "cumulative_users": np.percentile(sorted["cumulative_users"], percents)
    })
    display(opp_size)
