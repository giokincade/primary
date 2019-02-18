from datetime import date, datetime
from typing import Any, Dict

import numpy as np
import pandas as pd
from profilehooks import timecall


@timecall
def coerce_types(data: pd.DataFrame, types= Dict[str, Any]) -> pd.DataFrame:
    for col, tipe in types.items():
        if col in data:
            if tipe == str:
                data[col] = data[col].fillna("").astype(str)
            elif tipe == float or tipe == int:
                data[col] = data[col].replace("", np.nan).replace(
                    regex=r"[$,]", value=""
                ).astype(
                    float
                )
            elif tipe == date or tipe == datetime:
                data[col] = pd.to_datetime(data[col])
    return data
