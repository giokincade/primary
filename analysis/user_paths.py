from datetime import date
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats

from etl.events import get_events
from lib.constants import Colors, EventColumns, Events, UserColumns
from lib.viz import init_plt


def user_paths(
    users: pd.DataFrame,
    start: date = date(2018, 1, 1),
    end: date = date(2019, 1, 1),
    event_names: List[str] = [Events.PDP, Events.BAG, Events.CHECKOUT],
    palette: Dict[str, str] = {
        Events.PDP: Colors.PINK_MEDIUM,
        Events.BAG: Colors.YELLOW_LIGHT,
        Events.CHECKOUT: Colors.GREEN_MEDIUM,
    },
    x_jitter: float = None,
    y_jitter: float = None,
    title: str = "User Journeys",
):
    init_plt()
    events = get_events(list(users[EventColumns.EMAIL].values), start=start, end=end)
    users["user_index"] = range(1, len(users) + 1)
    events = events.join(
        users.set_index(UserColumns.EMAIL)[["user_index"]],
        on=UserColumns.EMAIL,
        how="inner",
    )
    events = events[events[EventColumns.NAME].isin(event_names)]
    events["epoch"] = events[EventColumns.TIME].apply( lambda d: d.timestamp())
    if x_jitter:
        events = _jitter(events, "epoch", x_jitter)
    if y_jitter:
        events = _jitter(events, "user_index", y_jitter)
    fig, ax = plt.subplots(figsize=(15, 10))
    sns.scatterplot(
        y="user_index",
        x="epoch",
        hue=EventColumns.NAME,
        palette=palette,
        hue_order=event_names,
        style=EventColumns.PLATFORM,
        ax=ax,
        data=events,
        s=75,
    )
    plt.gcf().suptitle(title)
    plt.ylabel("Individual User")
    plt.xlabel("Date")
    steps = pd.date_range(start, end, freq='MS').to_pydatetime()
    plt.xticks(
        [step.timestamp() for step in steps],
        [step.date().isoformat() for step in steps],
        rotation="vertical",
    )
    plt.legend(loc='center right', bbox_to_anchor=(1.25, 0.5), ncol=1)
    plt.yticks(list(range(1, len(users) + 1)))
    plt.show()


def _jitter(df: pd.DataFrame, col: str, jitter: float) -> pd.DataFrame:
    jitterer = stats.uniform(-jitter, jitter * 2).rvs(len(df))
    df[col] += jitterer
    return df
