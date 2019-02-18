from datetime import datetime
from io import StringIO
from unittest import TestCase
from unittest.mock import MagicMock as Mock
from unittest.mock import patch

import numpy as np
import pandas as pd

from etl.events import get_events
from lib.constants import EventColumns as Cols
from lib.constants import Events

_CSV = """
email,time,platform,name
gigi@gmail.com,2019-01-25,desktop,Product viewed
"""


class EventsTest(TestCase):

    @patch("etl.events.sql_to_df")
    def test_events(self, sql_mock: Mock):
        raw = pd.read_csv(StringIO(_CSV))
        sql_mock.return_value = raw
        events = get_events(["foo"])
        expected = pd.DataFrame(
            [["gigi@gmail.com", datetime(2019, 1, 25), "desktop", Events.PDP]],
            columns=[Cols.EMAIL, Cols.TIME, Cols.PLATFORM, Cols.NAME],
        )
        assert (expected.equals(events[expected.columns]))
