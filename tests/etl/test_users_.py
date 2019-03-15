from datetime import datetime
from io import StringIO
from unittest import TestCase
from unittest.mock import MagicMock as Mock
from unittest.mock import patch

import numpy as np
import pandas as pd

from etl.users import (
    _calculate_frequency_fields,
    _get_users_from_looker_export,
    _join_mixpanel_stats,
    get_users,
)
from lib.constants import UserColumns as Cols

_CSV = """
Customer Filters Email,Customer Segments First Order Cohort Date,Customer Segments Lifetime GPR,Customer Segments Lifetime Order Count,Customer Segments Lifetime Total Units
gigi@gmail.com,2019-01-25,"$1,041.00",1,5
"""


class UsersTest(TestCase):

    @patch("etl.users.read_csv")
    def test_get_users_from_looker_export(self, read_csv_mock: Mock):
        read_csv_mock.return_value = pd.read_csv(StringIO(_CSV))
        users = _get_users_from_looker_export.__wrapped__()
        expected = pd.DataFrame(
            [["gigi@gmail.com", datetime(2019, 1, 25), 1041.0, 1.0, 5.0]],
            columns=[
                Cols.EMAIL,
                Cols.FIRST_ORDER_DATE,
                Cols.LIFETIME_GPR,
                Cols.LIFETIME_ORDERS,
                Cols.LIFETIME_UNITS,
            ],
        )
        assert (expected.equals(users[expected.columns]))

    @patch("etl.users.read_csv")
    @patch("etl.users.sql_to_df")
    @patch("etl.users._get_users_from_looker_export")
    def test_users(
        self, _get_users_from_looker_export_mock: Mock,
        sql_to_df_mock: Mock,
        read_csv_mock: Mock
    ):
        read_csv_mock.return_value = pd.DataFrame([["gigi@gmail.com"]], columns=[Cols.EMAIL])
        _get_users_from_looker_export_mock.return_value = pd.DataFrame(
            [["gigi@gmail.com", datetime(2019, 1, 25), 1.0]],
            columns=[Cols.EMAIL, Cols.FIRST_ORDER_DATE, Cols.LIFETIME_ORDERS],
        )
        mixpanel = pd.DataFrame(
            [["gigi@gmail.com", 30, 2]],
            columns=[Cols.EMAIL, Cols.DAYS_RETAINED, Cols.DAYS_RETAINED_PER_VISIT],
        )
        first_order = pd.DataFrame(
            [["gigi@gmail.com", "kids"]],
            columns=[Cols.EMAIL, Cols.FIRST_ORDER_DIVISION],
        )
        sql_to_df_mock.side_effect = [mixpanel, first_order]
        users = get_users()
        expected = pd.DataFrame(
            [["gigi@gmail.com", datetime(2019, 1, 25), 1.0]],
            columns=[Cols.EMAIL, Cols.FIRST_ORDER_DATE, Cols.LIFETIME_ORDERS],
        )
        assert (expected.equals(users[expected.columns]))

    def test_calculate_frequency_fields(self):
        users = pd.DataFrame(
            [[2, 150]], columns=[Cols.LIFETIME_ORDERS, Cols.DAYS_RETAINED]
        )
        result = _calculate_frequency_fields(users)
        self.assertEqual([75.0], list(result[Cols.ORDER_FREQUENCY].values))

    @patch("etl.users.sql_to_df")
    def test_join(self, sql_to_df_mock: Mock):
        users = pd.DataFrame(
            [["foo@bar.com", 1], ["qux@bar.com", 2]],
            columns=[Cols.EMAIL, Cols.LIFETIME_ORDERS],
        )
        mixpanel = pd.DataFrame(
            [["foo@bar.com", 30, 2], ["hell@bar.com", 30, 2]],
            columns=[Cols.EMAIL, Cols.DAYS_RETAINED, Cols.DAYS_RETAINED_PER_VISIT],
        )
        sql_to_df_mock.return_value = mixpanel
        result = _join_mixpanel_stats(users).fillna(0.0)
        self.assertEqual([30.0, 0.0], list(result[Cols.DAYS_RETAINED].values))
