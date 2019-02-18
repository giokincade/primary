import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class Colors:
    WHITE = "#FFFFFF"
    PINK_LIGHT = "#F8A4A5"
    PINK_MEDIUM = "#FF6460"
    PINK_DARK = "#FF4E46"
    PURPLE_LIGHT = "#4D56AF"
    PURPLE_MEDIUM = "#3E4399"
    PURPLE_DARK = "#2B2877"
    GREEN_LIGHT = "#8FDCCD"
    GREEN_MEDIUM = "#4AC0A8"
    GREEN_DARK = "#38A58B"
    BLACK_LIGHT = "#9E9E9E"
    BLACK_MEDIUM = "#757575"
    BLACK_DARK = "#212121"
    GREY_LIGHT = "#F2EDE7"
    GREY_MEDIUM = "#CDC3BA"
    GREY_DARK = "#BDB4AB"
    YELLOW_DARK = "#FF7D00"
    YELLOW_MEDIUM = "#FFAA00"
    YELLOW_LIGHT = "#FEC300"


def init_plt():
    SMALL_SIZE = 14
    MEDIUM_SIZE = 18
    BIGGER_SIZE = 28
    plt.rc("font", size=SMALL_SIZE)
    plt.rc(
        "axes",
        titlesize=SMALL_SIZE,
        labelsize=MEDIUM_SIZE,
        labelpad=20,
        facecolor=Colors.GREY_LIGHT,
    )
    plt.rc("font", family="Proxima Nova", weight=500)
    plt.rc("xtick", labelsize=SMALL_SIZE)
    plt.rc("ytick", labelsize=SMALL_SIZE)
    plt.rc("legend", fontsize=SMALL_SIZE)
    plt.rc("figure", titlesize=BIGGER_SIZE, figsize=(15, 8), dpi=300)
    pd.options.display.float_format = "{:,.4f}".format
    pd.set_option("display.max_rows", 200)
    sns.set(
        rc={
            "figure.figsize": (15, 8),
            "figure.titlesize": BIGGER_SIZE,
            "figure.titleweight": 700,
            "font.family": "Proxima Nova",
            "xtick.labelsize": SMALL_SIZE,
            "ytick.labelsize": SMALL_SIZE,
            "legend.fontsize": SMALL_SIZE,
            "axes.titlesize": SMALL_SIZE,
            "axes.labelsize": MEDIUM_SIZE,
            "axes.labelweight": 700,
            "axes.labelpad": 20,
            "axes.facecolor": Colors.GREY_LIGHT,
        }
    )
    sns.set_palette(
        [
            Colors.GREEN_MEDIUM,
            Colors.PINK_MEDIUM,
            Colors.PURPLE_MEDIUM,
            Colors.YELLOW_DARK,
            Colors.GREEN_LIGHT,
            Colors.PINK_LIGHT,
            Colors.PURPLE_LIGHT,
            Colors.YELLOW_MEDIUM,
        ]
    )
