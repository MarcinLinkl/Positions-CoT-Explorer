import pandas as pd
from sodapy import Socrata
import sqlite3
from dotenv import load_dotenv
import os
from requests.exceptions import RequestException
from datetime import datetime

# Ustawienie opcji display.max_columns na None
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
load_dotenv()

# Credentials for Socrata API
APP_TOKEN = os.getenv("APP_TOKEN")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# # Initialize Socrata client
# socrata_client = Socrata(
#     "publicreporting.cftc.gov", APP_TOKEN, username=USERNAME, password=PASSWORD
# )

# For free None Api request, limit 20000


# Dictionary of report types and their corresponding identifiers
REPORTS = {
    "Legacy - Futures Only": "6dca-aqww",
    "Legacy - Combined": "jun7-fc8e",
    "Disaggregated - Futures Only": "72hh-3qpy",
    "Disaggregated - Combined": "kh3c-gbw2",
    "TFF - Futures Only": "gpe5-46if",
    "TFF - Combined": "yw9f-hn96",
    "Supplemental - CIT": "4zgm-a668",
}


def fetch_single_report(report_name):
    try:
        socrata_client = Socrata(
            "publicreporting.cftc.gov",
            None,
        )
        # Fetch data from the Socrata API and convert directly to pandas DataFrame
        data_records = pd.DataFrame.from_records(
            socrata_client.get(REPORTS[report_name], limit=9999999)
        )

        print(f"Number of records to be saved: {data_records.shape[0]}")

        # Identify numerical columns using `pd.to_numeric` and `notnull()` method
        numerical_columns = data_records.select_dtypes(include=[int, float]).columns

        # Convert numerical columns to numeric data type
        data_records[numerical_columns] = data_records[numerical_columns].apply(
            pd.to_numeric, errors="coerce"
        )
        # coerce all NaN values to None

        # Save data to SQLite database with appropriate table name
        # Remove spaces and replace "-" with "_" in the selected_report
        table_name = "report_" + "_".join(report_name.replace("-", "").split()).lower()

        with sqlite3.connect("data.db") as db_connection:
            data_records.to_sql(
                table_name, db_connection, if_exists="replace", index=False
            )
        print(f"Data successfully saved to the table '{table_name}' in the database.")
    except RequestException as e:
        print(f"An error occurred while fetching data: ", e)
    except pd.errors.EmptyDataError as e:
        print(f"An error occurred while processing data: ", e)
    except sqlite3.Error as e:
        print(f"An error occurred while saving to database: ", e)
    except Exception as e:
        print(f"An error occurred while processing data: ", e)


# Call the function to fetch data for all reports
def fetch_all_reports():
    for report_name in REPORTS:
        fetch_single_report(report_name)


# fetch_single_report("Legacy - Futures Only")


# def create_tickers_table():
#     with sqlite3.connect("data.db") as db_connection:
#         db_cursor = db_connection.cursor()
#         db_cursor.execute(
#             """
#             CREATE TABLE IF NOT EXISTS tickers_yahoo (
#                 id INTEGER PRIMARY KEY,
#                 commodity TEXT,
#                 market_and_exchange_names TEXT,
#                 yahoo_name TEXT,
#                 yahoo_ticker TEXT

#             )
#         """
#         )


# def populate_tickers_table_from_report_table(report_table_name):
#     print("Populating tickers_yahoo table from report table...")
#     with sqlite3.connect("data.db") as db_connection:
#         db_cursor = db_connection.cursor()
#         # Check if the tickers_yahoo table is empty
#         db_cursor.execute("SELECT COUNT(*) FROM tickers_yahoo")
#         count = db_cursor.fetchone()[0]
#         if count == 0:
#             # Fetch all unique market_and_exchange_names from all report tables

#             print(
#                 "Fetching all unique market_and_exchange_names from all report tables..."
#             )
#             query = f"""
#                 SELECT DISTINCT commodity,market_and_exchange_names
#                 FROM {report_table_name}
#                 WHERE yyyy_report_week_ww like '%{datetime.now().year}%'
#             """
#             print(query)
#             db_cursor.execute(query)

#             unique_market_names = db_cursor.fetchall()
#             print(len(unique_market_names))

#             # Populate tickers_yahoo table with missing market data
#             for i in unique_market_names:
#                 print("inserting: ", i[1])

#                 db_cursor.execute(
#                     """
#                     INSERT INTO tickers_yahoo (commodity,market_and_exchange_names, yahoo_name, yahoo_ticker)
#                     VALUES (?, ?, ?, ?)
#                 """,
#                     (i[0], i[1], None, None),
#                 )


# create_tickers_table()
# populate_tickers_table_from_report_table("report_legacy_futures_only")

fetch_all_reports()
