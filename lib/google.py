import gspread
import gspread_dataframe as gd
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from lib.settings import BASE_DIR


def _get_google_client():
    scope = [
        "https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"
    ]
    path = BASE_DIR + "/google.json"
    creds = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
    return gspread.authorize(creds)


def df_to_google(data: pd.DataFrame, spreadsheet: str, worksheet: str):
    google = _get_google_client()
    sheet = google.open(spreadsheet).worksheet(worksheet)
    return gd.set_with_dataframe(sheet, data)


def google_to_df(spreadsheet: str, worksheet: str, *args, **kwargs) -> pd.DataFrame:
    google = _get_google_client()
    sheet = google.open(spreadsheet).worksheet(worksheet)
    return gd.get_as_dataframe(sheet, *args, **kwargs)
