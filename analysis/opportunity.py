from datetime import date

import pandas as pd
from IPython.core.display import HTML, display

from lib.sql import sql_to_df

"""Tuples of (strategy, page, opp_name, segment, lift)"""
OPPORTUNITY_MAP = [
    ('Delight Inspiration', 'product', 'Shop the Look', 'all_users', 0.02),
    ('Delight Inspiration', 'product', 'Outfits Module', 'all_users', 0.03),
    ('Delight Inspiration', 'product', 'Pairs Well With  Module', 'all_users', 0.02),
    ('Delight Inspiration', 'product', 'Similar Items Module', 'all_users', 0.01),
    ('Delight Inspiration', 'bag', 'Goes well with Module', 'all_users', 0.02),
    ('Delight Inspiration', 'bag', 'Don\'t Forget Basics Module', 'all_users', 0.01),
    ('Delight Inspiration', 'bag', 'Overlay Recommendations', 'all_users', 0.02),
    (
        'Utilitarian Inspiration',
        'product',
        'Previous Order Reminder',
        'prior_transaction_same_product',
        0.05,
    ),
    (
        'Utilitarian Inspiration',
        'product',
        'Reorder Module',
        'prior_transaction_same_product',
        0.05,
    ),
    ('Utilitarian Inspiration', 'product', 'Bundle Builder', 'all_users', 0.02),
    ('Utilitarian Inspiration', 'product', 'Recently Viewed', 'all_users', 0.02),
    ('Utilitarian Inspiration', 'bag', 'Reorder Module', 'prior_transaction', 0.05),
    ('Utilitarian Inspiration', 'bag', 'Recently Viewed', 'all_users', 0.02),
    (
        'Utilitarian Inspiration',
        'product_list',
        'Previously Purchased Badges and Filter',
        'prior_transaction',
        0.05,
    ),
    (
        'Reduce Friction',
        'product',
        'Size/Color Hints',
        'prior_transaction_same_product',
        0.05,
    ),
    (
        'Reduce Friction',
        'checkout_start',
        'Repeat Purchaser Fast Forward',
        'prior_transaction',
        0.05,
    ),
    ('Reduce Friction', 'bag', 'Apple Pay', 'all_users', 0.03),
    ('Urgency', 'product', 'Only X Left', 'all_users', 0.01),
    ('Urgency', 'bag', 'Only X Left', 'all_users', 0.01),
    ('Inspiration', 'home', 'Return Visitor Home Page', 'prior_transaction', 0.05),
]


def opportunity_sizes(
    start: date = date(2018, 12, 1), end: date = date(2019, 2, 25), aov=60
):
    raw_data = sql_to_df("conversions_per_page.sql", start=start, end=end)
    raw_data["avg_daily_users"] = raw_data["avg_daily_users"].astype(float)
    raw_data["avg_user_conversion_rate"] = raw_data["avg_user_conversion_rate"].astype(
        float
    )
    display(HTML("<h1>Event + Segment Data</h1>"))
    display(raw_data)
    results = []
    for strategy, event, opp_name, segment, lift in OPPORTUNITY_MAP:
        raw_data_row = raw_data[
            (raw_data["event"] == event) & (raw_data["segment"] == segment)
        ].iloc[
            0
        ]
        avg_daily_users = raw_data_row["avg_daily_users"]
        avg_conversion_rate = raw_data_row["avg_user_conversion_rate"]
        delta = avg_conversion_rate * lift
        new_conversions_daily = avg_daily_users * delta
        new_conversions_yearly = new_conversions_daily * 365
        new_revenue_yearly = new_conversions_yearly * aov
        results.append(
            {
                "strategy": strategy,
                "page": event,
                "opportunity": opp_name,
                "segment": segment,
                "avg_daily_users": avg_daily_users,
                "avg_conversion_rate": avg_conversion_rate,
                "projected_lift": lift,
                "delta": delta,
                "new_conversions_daily": new_conversions_daily,
                "new_conversions_yearly": new_conversions_yearly,
                "new_revenue_yearly": new_revenue_yearly,
            }
        )
    opps = pd.DataFrame.from_records(results)[
        [
            "strategy",
            "page",
            "opportunity",
            "segment",
            "avg_daily_users",
            "avg_conversion_rate",
            "projected_lift",
            "delta",
            "new_conversions_daily",
            "new_conversions_yearly",
            "new_revenue_yearly",
        ]
    ]
    display(HTML("<h1>Opportunities</h1>"))
    display(opps)
    return opps
