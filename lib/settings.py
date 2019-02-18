import os

BASE_DIR = "/home/jovyan/"
SQL_DIR = BASE_DIR + "sql/"
CACHE_DIR = BASE_DIR + "/.disk_cache/"
STATIC_DATA_DIR = BASE_DIR + "/static_data/"
DATA_DIR = BASE_DIR + "/data/"
SNOWFLAKE_USER = os.environ.get("SNOWFLAKE_USER", None)
SNOWFLAKE_PASSWORD = os.environ.get("SNOWFLAKE_PASSWORD", None)
SNOWFLAKE_ACCOUNT = "ui36489.us-east-1"
SNOWFLAKE_DATABASE = "PRIMARYDB"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
LOOKER_CLIENT_ID = os.environ.get("LOOKER_CLIENT_ID", None)
LOOKER_SECRET = os.environ.get("LOOKER_SECRET", None)
