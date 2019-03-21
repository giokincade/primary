from datetime import date
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from lib.constants import TransactionColumns, UserColumns
from lib.sql import sql_to_df
from lib.viz import Colors, init_plt


def order_frequency(users: pd.DataFrame):
    init_plt()
    sns.lineplot(
        x=UserColumns.FIRST_ORDER_MONTH,
        y=UserColumns.FIRST_ORDER_MONTH,
        estimator= lambda x: len(x),
        data=users,
    )
    plt.gcf().suptitle("Users Acquired by Date")
    plt.xlabel("First Order Date")
    plt.ylabel("Users")
    plt.show()
    sns.distplot(users[UserColumns.LIFETIME_ORDERS], kde=False)
    plt.gcf().suptitle("Lifetime Orders")
    plt.xlabel("Lifetime Orders")
    plt.ylabel("Users")
    plt.show()
    candidates = users[
        (users[UserColumns.LIFETIME_ORDERS] > 1) &
        (~ users[UserColumns.AVG_DAYS_BETWEEN_ORDERS].isna()) &
        (~ users[UserColumns.AVG_DAYS_BETWEEN_VISITS].isna())
    ].copy(
    )
    sns.distplot(candidates[UserColumns.LIFETIME_ORDERS], kde=False)
    plt.gcf().suptitle("Lifetime Orders > 1")
    plt.xlabel("Lifetime Orders")
    plt.ylabel("Users")
    plt.show()
    sns.distplot(
        users[UserColumns.LIFETIME_ORDERS],
        bins=[0, 1, 2, 3, 5, 10, 15, 20, 30, 100],
        hist_kws=dict(cumulative=True),
    )
    plt.gcf().suptitle("Lifetime Orders CDF < 20")
    plt.xlabel("Lifetime Orders")
    plt.ylabel("CDF")
    plt.xticks([1, 2, 3, 5, 10, 15, 20, 30, 100])
    plt.xlim(0, 20)
    plt.show()
    sns.distplot(candidates[UserColumns.AVG_DAYS_BETWEEN_ORDERS], kde=False)
    plt.gcf().suptitle("Average Days Between Orders")
    plt.xlabel("Average Days Between Ordres")
    plt.ylabel("Users")
    plt.show()
    sns.distplot(
        candidates[UserColumns.AVG_DAYS_BETWEEN_ORDERS], hist_kws=dict(cumulative=True)
    )
    plt.gcf().suptitle("Average Days Between Orders < 300 CDF")
    plt.xlabel("Average Days Between Orders")
    plt.ylabel("CDF")
    plt.xlim(0, 300)
    plt.show()
    sns.countplot(candidates[UserColumns.FIRST_ORDER_DIVISION])
    plt.gcf().suptitle("Users by First Order Division")
    plt.xlabel("Division")
    plt.ylabel("Users")
    plt.show()
    sns.distplot(candidates[UserColumns.AVG_DAYS_BETWEEN_VISITS], kde=False)
    plt.gcf().suptitle("Average Days Between Visits")
    plt.xlabel("Average Days Between Visits")
    plt.ylabel("Users")
    plt.show()
    sns.distplot(
        candidates[UserColumns.AVG_DAYS_BETWEEN_VISITS], hist_kws=dict(cumulative=True)
    )
    plt.gcf().suptitle("Average Days Between Visits CDF")
    plt.xlabel("Average Days Between Visits")
    plt.ylabel("CDF")
    plt.xlim(0, 300)
    plt.show()
    melted = pd.melt(
        candidates,
        id_vars=[
            UserColumns.EMAIL,
            UserColumns.LIFETIME_ORDERS,
            UserColumns.FIRST_ORDER_DIVISION,
        ],
        value_vars=[
            UserColumns.AVG_DAYS_BETWEEN_ORDERS, UserColumns.AVG_DAYS_BETWEEN_VISITS
        ],
    )
    melted["variable"] = melted["variable"].apply(
        lambda v: "orders" if v == UserColumns.AVG_DAYS_BETWEEN_ORDERS else "visits"
    )
    sns.lineplot(x=UserColumns.LIFETIME_ORDERS, y="value", hue="variable", data=melted)
    plt.gcf().suptitle("Days between Events by Lifetime Orders")
    plt.ylabel("Days between Events")
    plt.xlabel("Lifetime Orders")
    plt.xlim(2, 10)
    plt.show()
    sns.lineplot(
        x=UserColumns.LIFETIME_ORDERS,
        y="value",
        hue="variable",
        style=UserColumns.FIRST_ORDER_DIVISION,
        data=melted[melted[UserColumns.FIRST_ORDER_DIVISION] != "unknown"],
    )
    plt.gcf().suptitle("Days between Events by Lifetime Orders")
    plt.ylabel("Days between Events")
    plt.xlabel("Lifetime Orders")
    plt.xlim(2, 10)
    plt.show()


def order_frequency_over_time(users: pd.DataFrame):
    init_plt()
    candidates = users[
        (users[UserColumns.LIFETIME_ORDERS] > 1) &
        (~ users[UserColumns.AVG_DAYS_BETWEEN_ORDERS].isna()) &
        (~ users[UserColumns.AVG_DAYS_BETWEEN_VISITS].isna())
    ]


def common_products(transactions: pd.DataFrame):
    init_plt()
    candidates = transactions[transactions[TransactionColumns.ORDER_INDEX] > 1.0][
        [
            TransactionColumns.ORDER_ID,
            TransactionColumns.ORDER_INDEX,
            TransactionColumns.COMMON_PRODUCTS_RATIO,
        ]
    ].copy(
    )
    candidates["order_number"] = pd.cut(
        candidates[TransactionColumns.ORDER_INDEX],
        bins=[2, 3, 4, 5, 100],
        labels=["2", "3", "4", "5+"],
        right=False,
        include_lowest=True,
    )
    candidates["product_ratio_bucket"] = pd.cut(
        candidates[TransactionColumns.COMMON_PRODUCTS_RATIO],
        bins=list(range(0, 91, 10)) + [101],
        labels=[
            "0-9",
            "10-19",
            "20-29",
            "30-39",
            "40-49",
            "50-59",
            "60-69",
            "70-79",
            "80-89",
            "90-100",
        ],
        right=False,
        include_lowest=True,
    )
    order_buckets = candidates.groupby("order_number").size().rename(
        "order_number_total"
    )
    grouped = candidates.groupby(["order_number", "product_ratio_bucket"]).size(
    ).rename(
        "transactions"
    )
    grouped = grouped.to_frame().join(order_buckets, on="order_number").reset_index()
    grouped["percentage"] = grouped["transactions"] / grouped[
        "order_number_total"
    ] * 100.0
    sns.barplot(
        x="product_ratio_bucket", y="percentage", hue="order_number", data=grouped
    )
    plt.ylabel("% of Orders")
    plt.xlabel("% of Previously Purchased Styles per Order")
    plt.xticks(rotation="vertical")
    plt.gcf().suptitle("Previously Purchased Styles in Repeat Orders")
    plt.show()


def quality_onetimers(users: pd.DataFrame):
    init_plt()
    candidates = users[
        (users[UserColumns.LIFETIME_ORDERS] < 2) &
        (users[UserColumns.LIFETIME_GPR] > 90.0)
    ].copy(
    )
    candidates["month"] = candidates[UserColumns.FIRST_ORDER_MONTH].apply(
        lambda d: d.month
    )
    sns.lineplot(
        x=UserColumns.FIRST_ORDER_MONTH,
        y=UserColumns.FIRST_ORDER_MONTH,
        estimator= lambda x: len(x),
        data=users,
    )
    plt.gcf().suptitle("Quality Onetimers by Date")
    plt.xlabel("First Order Date")
    plt.ylabel("Users")
    plt.show()
    grouped = candidates.groupby("month").agg({"email": "count"}).rename(
        columns={"email": "users"}
    )
    grouped["percentage"] = grouped["users"] / len(candidates) * 100.0
    grouped.plot(y="percentage", kind="bar", color=Colors.GREEN_LIGHT)
    plt.gcf().suptitle("Quality Onetimers by Month")
    plt.xlabel("First Order Month")
    plt.ylabel("% of Users")
    plt.show()


def guest_users(transactions: pd.DataFrame):
    init_plt()
    is_guest = TransactionColumns.IS_GUEST
    users = transactions.groupby(TransactionColumns.EMAIL).agg(
        {
            is_guest: "max",
            TransactionColumns.ORDER_ID: "count",
            TransactionColumns.ITEM_TOTAL: "mean",
        }
    ).rename(
        columns={
            TransactionColumns.ORDER_ID: "orders", TransactionColumns.ITEM_TOTAL: "aov"
        }
    )
    users["order_count_bucket"] = pd.cut(
        users["orders"],
        bins=[1, 2, 3, 4, 5, 6, 11, users["orders"].max() + 1],
        labels=["1", "2", "3", "4", "5", "6-10", "11+"],
        right=False,
    )
    users["aov_bucket"] = pd.cut(
        users["aov"],
        bins=[0, 50, 101, users["aov"].max() + 1],
        labels=["<50", "50-100", "100+"],
        right=False,
    )
    guest_group = users.groupby(TransactionColumns.IS_GUEST).size().rename(
        "is_guest_transactions"
    )
    grouped = users.groupby(["order_count_bucket", is_guest]).size().rename(
        "transactions"
    ).to_frame(
    ).reset_index(
    )
    grouped = grouped.join(guest_group, on=is_guest)
    grouped["percentage"] = grouped["transactions"] / grouped[
        "is_guest_transactions"
    ] * 100.0
    sns.barplot(
        x="order_count_bucket", y="percentage", hue=is_guest, data=grouped, ci=False
    )
    plt.gcf().suptitle("Lifetime Orders by Signed-In vs Guest")
    plt.xlabel("Lifetime Orders")
    plt.ylabel("% of Users")
    plt.legend(plt.legend().get_patches(), ["signed_in", "guest"])
    plt.show()
    guest_counts = users[users[TransactionColumns.IS_GUEST] > 0.0].groupby(
        ["aov_bucket", "order_count_bucket"]
    ).size(
    ).rename(
        "guest_users"
    ).to_frame(
    )
    matrix = users.groupby(["aov_bucket", "order_count_bucket"]).size().rename(
        "users"
    ).to_frame(
    )
    matrix = matrix.join(guest_counts, how="left").fillna(0.0)
    matrix["guest_percentage"] = matrix["guest_users"] / matrix["users"]
    graph = matrix["guest_percentage"].unstack().T
    display(graph)
    sns.heatmap(graph, cmap=sns.light_palette(Colors.PINK_DARK), annot=True)
    plt.gcf().axes[0].invert_yaxis()
    plt.gcf().suptitle("Guest User Penetration by AOV and Lifetime Orders")
    plt.xlabel("AOV")
    plt.ylabel("Lifetime Orders")
    plt.show()


def sales(transactions: pd.DataFrame):
    init_plt()
    sale_transactions = transactions[transactions[TransactionColumns.HAS_SALE_ITEM] > 0]
    sale_transactions.groupby(TransactionColumns.ORDER_MONTH).size().rename(
        "orders"
    ).to_frame(
    ).plot(
        y="orders", kind="bar"
    )
    plt.gcf().suptitle("Sale Orders by Date")
    plt.ylabel("Sale Orders")
    plt.xlabel("Date")
    plt.show()
    users = transactions.groupby(TransactionColumns.EMAIL).agg(
        {
            TransactionColumns.HAS_SALE_ITEM: "sum",
            TransactionColumns.ORDER_ID: "count",
            TransactionColumns.ITEM_TOTAL: "mean",
        }
    ).rename(
        columns={
            TransactionColumns.HAS_SALE_ITEM: "sale_orders",
            TransactionColumns.ORDER_ID: "orders",
            TransactionColumns.ITEM_TOTAL: "aov",
        }
    )
    users["order_count_bucket"] = pd.cut(
        users["orders"],
        bins=[1, 2, 3, 4, 5, 6, 11, users["orders"].max() + 1],
        labels=["1", "2", "3", "4", "5", "6-10", "11+"],
        right=False,
    )
    users["aov_bucket"] = pd.cut(
        users["aov"],
        bins=[0, 50, 101, users["aov"].max() + 1],
        labels=["<50", "50-100", "100+"],
        right=False,
    )
    heatmap = users.groupby(["order_count_bucket", "aov_bucket"]).sum()[
        "sale_orders"
    ].unstack(
    ).fillna(
        0
    ).astype(
        int
    )
    sns.heatmap(heatmap, cmap=sns.light_palette(Colors.PINK_DARK), annot=True, fmt=",")
    plt.gcf().axes[0].invert_yaxis()
    plt.gcf().suptitle("Orders w/ a Sale Item")
    plt.xlabel("User AOV")
    plt.ylabel("User Lifetime Orders")
    plt.show()


def units_per_order(transactions: pd.DataFrame):
    init_plt()
    cols = TransactionColumns
    units = cols.UNITS
    repeats = transactions[transactions[cols.IS_REPEAT] > 0.0]
    sns.distplot(transactions[units], kde=False)
    plt.gcf().suptitle("Units per Order")
    plt.xlabel("Units per Order")
    plt.ylabel("Orders")
    plt.show()
    sns.distplot(repeats[units], kde=False)
    plt.gcf().suptitle("Units per Repeat Order")
    plt.xlabel("Units per Order")
    plt.ylabel("Repeat Orders")
    plt.show()
    sns.lineplot(x=cols.ORDER_DATE, y=cols.UNITS, hue=cols.IS_REPEAT, data=transactions)
    plt.ylim(0, 10)
    plt.legend(plt.legend().get_patches(), ["first_order", "repeat_order"])
    plt.gcf().suptitle("Units per Order")
    plt.xlabel("Date")
    plt.ylabel("Average Units Per Order")
    plt.show()


def products_per_bag(start: date = date(2018, 12, 1), end: date = date(2019, 2, 25)):
    init_plt()
    user_date_stats = sql_to_df('views_per_bag.sql', start=start, end=end)
    user_date_stats["bag_indicator"] = user_date_stats["bag_indicator"].astype(float)
    sns.lineplot(x="product", y="bag_indicator", data=user_date_stats)
    plt.gcf().suptitle("Product Views vs Bags")
    plt.xlabel("Product Views")
    plt.ylabel("Likelihood of Bagging")
    plt.xlim(0, 25)
    plt.show()


def days_between_events_by_lifetime_orders(users: pd.DataFrame):
    candidates = users[
        (users[UserColumns.LIFETIME_ORDERS] > 1) &
        (~ users[UserColumns.AVG_DAYS_BETWEEN_ORDERS].isna()) &
        (~ users[UserColumns.AVG_DAYS_BETWEEN_VISITS].isna())
    ].copy(
    )
    melted = pd.melt(
        candidates,
        id_vars=[
            UserColumns.EMAIL,
            UserColumns.LIFETIME_ORDERS,
            UserColumns.FIRST_ORDER_DIVISION,
        ],
        value_vars=[
            UserColumns.AVG_DAYS_BETWEEN_ORDERS, UserColumns.AVG_DAYS_BETWEEN_VISITS
        ],
    )
    melted["variable"] = melted["variable"].apply(
        lambda v: "orders" if v == UserColumns.AVG_DAYS_BETWEEN_ORDERS else "visits"
    )
    sns.lineplot(x=UserColumns.LIFETIME_ORDERS, y="value", hue="variable", data=melted)
    plt.gcf().suptitle("Days between Events by Lifetime Orders")
    plt.ylabel("Days between Events")
    plt.xlabel("Lifetime Orders")
    plt.xlim(2, 10)
    plt.show()

def pilot_user_heatmap(users: pd.DataFrame):
    init_plt()
    heatmap = users.groupby([UserColumns.LIFETIME_ORDERS_BUCKET, UserColumns.LIFETIME_AOV_BUCKET]).sum()[
        UserColumns.IS_PICKS_BUYER
    ].unstack(
    ).fillna(
        0
    ).astype(
        int
    )

    sns.heatmap(heatmap, cmap=sns.light_palette(Colors.PINK_DARK), annot=True, fmt=",")
    plt.gcf().axes[0].invert_yaxis()
    plt.gcf().suptitle("Pilot Box Users")
    plt.xlabel("User AOV")
    plt.ylabel("User Lifetime Orders")
    plt.show()

    heatmap = users.groupby([UserColumns.ORDERS_PER_QUARTER_BUCKET, UserColumns.LIFETIME_AOV_BUCKET]).sum()[
        UserColumns.IS_PICKS_BUYER
    ].unstack(
    ).fillna(
        0
    ).astype(
        int
    )

    sns.heatmap(heatmap, cmap=sns.light_palette(Colors.PINK_DARK), annot=True, fmt=",")
    plt.gcf().axes[0].invert_yaxis()
    plt.gcf().suptitle("Pilot Box Users")
    plt.xlabel("AOV")
    plt.ylabel("Orders per Quarter")
    plt.show()

def marketing_opt_out(users: pd.DataFrame):
    init_plt()
    heatmap = users.groupby([UserColumns.LIFETIME_ORDERS_BUCKET, UserColumns.LIFETIME_AOV_BUCKET]).sum()[
        UserColumns.IS_MARKETING_OPT_OUT
    ].unstack(
    ).fillna(
        0
    ).astype(
        int
    )

    sns.heatmap(heatmap, cmap=sns.light_palette(Colors.PINK_DARK), annot=True, fmt=",")
    plt.gcf().axes[0].invert_yaxis()
    plt.gcf().suptitle("Marketing Opt-Out Users")
    plt.xlabel("AOV")
    plt.ylabel("Lifetime Orders")
    plt.show()

    total_users_heatmap = users.groupby(
        [UserColumns.LIFETIME_ORDERS_BUCKET, UserColumns.LIFETIME_AOV_BUCKET]
    ).count(
    )[UserColumns.EMAIL].unstack(
    ).fillna(
        0
    ).astype(
        int
    )
    percentage_map = heatmap / total_users_heatmap

    sns.heatmap(
        percentage_map,
        cmap=sns.light_palette(Colors.PINK_DARK),
        annot=True,
        fmt=".0%"
    )
    plt.gcf().axes[0].invert_yaxis()
    plt.gcf().suptitle("Marketing Opt-Out Users")
    plt.xlabel("AOV")
    plt.ylabel("Lifetime Orders")
    plt.show()

    heatmap = users.groupby(
        [UserColumns.ORDERS_PER_QUARTER_BUCKET, UserColumns.LIFETIME_AOV_BUCKET]
    ).sum()[
        UserColumns.IS_MARKETING_OPT_OUT
    ].unstack(
    ).fillna(
        0
    ).astype(
        int
    )

    sns.heatmap(heatmap, cmap=sns.light_palette(Colors.PINK_DARK), annot=True, fmt=",")
    plt.gcf().axes[0].invert_yaxis()
    plt.gcf().suptitle("Marketing Opt-Out Users")
    plt.xlabel("AOV")
    plt.ylabel("Orders per Quarter")
    plt.show()
