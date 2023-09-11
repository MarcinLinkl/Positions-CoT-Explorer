import pandas as pd
from requests import ReadTimeout
from sodapy import Socrata
from reports_cols import (
    report_api_cols,
    main_api_cols,
    root_cols,
)
import sqlite3
from datetime import datetime as dt
from requests.exceptions import Timeout

REPORTS_TABLE = {
    "report_legacy_futures_only": "6dca-aqww",
    "report_legacy_combined": "jun7-fc8e",
    "report_disaggregated_futures_only": "72hh-3qpy",
    "report_disaggregated_combined": "kh3c-gbw2",
    "report_tff_futures_only": "gpe5-46if",
    "report_tff_combined": "yw9f-hn96",
}

REPORTS = {
    "Legacy - Futures Only": "6dca-aqww",
    "Legacy - Combined": "jun7-fc8e",
    "Disaggregated - Futures Only": "72hh-3qpy",
    "Disaggregated - Combined": "kh3c-gbw2",
    "TFF - Futures Only": "gpe5-46if",
    "TFF - Combined": "yw9f-hn96",
}


# all report saving
def fetch_all_reports():
    for report_name in REPORTS:
        fetch_single_report(report_name)


def fetch_new_all(last_week):
    with sqlite3.connect("data.db") as conn:
        query = (
            "SELECT name FROM sqlite_schema WHERE type='table' AND name LIKE 'report_%'"
        )
        tables = conn.execute(query).fetchall()[0]
    for report_table in tables:
        fetch_new_report(report_table, last_week)


def fetch_new_report(report_table_name, last_week):
    report_root_name = report_table_name.split("_")[1]

    # Create a comma-separated list of selected columns for the API query
    selected_columns = ",".join(main_api_cols + report_api_cols[report_root_name])

    socrata_client = Socrata("publicreporting.cftc.gov", None)
    try:
        print("Making connection to socrata API...")
        # Fetch data from the Socrata API for the specified reporting year range and convert to a pandas DataFrame
        data_records = pd.DataFrame.from_records(
            socrata_client.get(
                REPORTS_TABLE[report_table_name],
                select=selected_columns,
                where=f"yyyy_report_week_ww > '{last_week}'",
                limit=999999,
            )
        )

        # Print the number of records fetched
        print(f"Number of records fetched: {data_records.shape[0]}")

        if not data_records.empty:
            print("New data found...")
            print(f"Number of records fetched: {data_records.shape[0]}")
            with sqlite3.connect("data.db") as db_connection:
                # Create the 'cftc_codes' table if it doesn't exist
                cursor = db_connection.cursor()
                cursor.execute(
                    f"""
                    select cftc_contract_market_code from cftc_codes where {report_table_name}=1   
                """
                )
                codes_CFTC = cursor.fetchall()[0]

            # filtering data_records based on the condition
            data_records = data_records[
                data_records["cftc_contract_market_code"].isin(codes_CFTC)
            ]
            # Print the number of records prepared to save in db
            print(f"Number of records to be saved: {data_records.shape[0]}")

            # Convert column names to lowercase, remove the "_all" suffix, and replace "__" with "_"
            data_records.columns = [
                col.lower().replace("_all", "").replace("__", "_")
                for col in data_records.columns
            ]

            # Delete 'market_and_exchange_names' and 'commodity' columns (only 'cftc_codes' will be used)
            data_records.drop(
                [
                    "market_and_exchange_names",
                    "commodity",
                    "commodity_subgroup_name",
                    "contract_units",
                ],
                axis=1,
                inplace=True,
            )

            # change to numeric data values for saving properly types
            df_1 = data_records.iloc[:, :3]
            df_2 = data_records.iloc[:, 3:].apply(pd.to_numeric, errors="coerce")
            data_records = pd.concat([df_1, df_2], axis=1)

            # calc net positions
            for root in root_cols[report_root_name]:
                print("Calculating net data for: " + root)
                data_records[f"{root}_net"] = data_records.apply(
                    lambda row: row[f"{root}_long"] - row[f"{root}_short"], axis=1
                )

            # Replace NaN values with None
            data_records = data_records.where(pd.notna(data_records), None)

            # Save data to the 'data.db' database else rise exception
            with sqlite3.connect("data.db") as db_connection:
                try:
                    data_records.to_sql(
                        report_table_name,
                        db_connection,
                        if_exists="append",
                        index=False,
                    )
                    print(
                        f"Data successfully saved to the table '{report_table_name}' in the database."
                    )

                except Exception as e:
                    print(
                        f"Failed to save data to the table '{report_table_name}' in the database. Error: {str(e)}"
                    )
        else:
            print("No new report found.")
    except ConnectionError:
        # Handle the timeout exception
        print("Timeout: Failed to fetch data from the Socrata API.")
        print("Please try again later, or may try to use other IP adress.")
    except Exception as e:
        # Handle other unexpected exceptions
        print(f"Error occurred: {e}")


def fetch_single_report(report_name, data_presence_years_back=5):
    # Create a Socrata client
    socrata_client = Socrata("publicreporting.cftc.gov", None)
    report_main = report_name.split()[0].lower()

    # Select the specific columns you want to fetch from the API
    selected_columns = main_api_cols + report_api_cols[report_main]

    # Create a comma-separated list of selected columns for the API query
    selected_columns_query = ",".join(selected_columns)

    try:
        print("Connecting to socrata API...")
        data_records = pd.DataFrame.from_records(
            socrata_client.get(
                REPORTS[report_name],
                select=selected_columns_query,
                limit=999999,
            )
        )
        # Print the number of records fetched
        print(f"Number of records fetched: {data_records.shape[0]}")

        # fin  data codes spanning over the last 5 years
        codes_CFTC = find_common_codes(data_records, data_presence_years_back)

        # Filter for data spanning code years back
        data_records = data_records[
            data_records["cftc_contract_market_code"].isin(codes_CFTC)
        ]

        # Print the number of records after filter for data spanning for specific number of years back
        print(
            f"After filtering for data spanning over {data_presence_years_back} years, the number of records to be saved is: {data_records.shape[0]}"
        )

        # Convert column names to lowercase, remove the "_all" suffix, and replace "__" with "_"
        data_records.columns = [
            col.lower().replace("_all", "").replace("__", "_")
            for col in data_records.columns
        ]

        # Create a table name based on the report name
        report_table = "report_" + "_".join(
            report_name.replace("- ", "").lower().split()
        )

        # insert the report_id and report_name
        with sqlite3.connect("data.db") as db_connection:
            # Create the 'cftc_codes' table if it doesn't exist
            db_connection.execute(
                """CREATE TABLE IF NOT EXISTS cftc_codes (
                    cftc_contract_market_code TEXT PRIMARY KEY UNIQUE,
                    commodity TEXT,
                    commodity_subgroup_name TEXT,
                    market_and_exchange_names TEXT,
                    report_legacy_futures_only INTEGER DEFAULT 0,
                    report_legacy_combined INTEGER DEFAULT 0,
                    report_disaggregated_futures_only INTEGER DEFAULT 0,
                    report_disaggregated_combined INTEGER DEFAULT 0,
                    report_tff_futures_only INTEGER DEFAULT 0,
                    report_tff_combined INTEGER DEFAULT 0,
                    contract_units TEXT
                )"""
            )

            # Save unique CFTC Contract Market Codes and their names to the 'cftc_codes' table
            existing_codes_query = (
                "SELECT DISTINCT cftc_contract_market_code FROM cftc_codes"
            )

            existing_codes = set(
                pd.read_sql(existing_codes_query, db_connection)[
                    "cftc_contract_market_code"
                ]
            )

            # Find new unique CFTC Contract Market Codes tha not exist in db
            unique_new_codes = codes_CFTC - existing_codes

            if unique_new_codes:
                df_cftc_codes = (
                    data_records[
                        data_records["cftc_contract_market_code"].isin(unique_new_codes)
                    ]
                    .groupby("cftc_contract_market_code", as_index=False)
                    .agg(
                        {
                            "commodity": "first",
                            "contract_units": "first",
                            "market_and_exchange_names": "first",
                            "commodity_subgroup_name": "first",
                        }
                    )
                )

                # Append new unique CFTC Contract Market Codes and their names to 'cftc_codes' table
                df_cftc_codes.to_sql(
                    "cftc_codes", db_connection, if_exists="append", index=False
                )
                print(
                    f"New unique CFTC Contract Market Codes - {len(unique_new_codes)} - saved to cftc_codes table."
                )

        with sqlite3.connect("data.db") as db_connection:
            codes_CFTC = [str(code) for code in codes_CFTC]
            query = f"UPDATE cftc_codes SET {report_table} = True WHERE cftc_contract_market_code IN ({', '.join('?' for _ in codes_CFTC)})"
            db_connection.execute(query, codes_CFTC)

        # Delete 'market_and_exchange_names' and 'commodity' columns (only 'cftc_codes' will be used)
        data_records.drop(
            [
                "market_and_exchange_names",
                "commodity",
                "commodity_subgroup_name",
                "contract_units",
            ],
            axis=1,
            inplace=True,
        )

        # change to numeric data values for saving properly types
        df_1 = data_records.iloc[:, :3]
        df_2 = data_records.iloc[:, 3:].apply(pd.to_numeric, errors="coerce")
        data_records = pd.concat([df_1, df_2], axis=1)

        # calc net positions
        for root in root_cols[report_main]:
            print("Calculating net data for: " + root)
            data_records[f"{root}_net"] = data_records.apply(
                lambda row: row[f"{root}_long"] - row[f"{root}_short"], axis=1
            )

        # Replace NaN values with None
        data_records = data_records.where(pd.notna(data_records), None)

        # Save data to the 'data.db' database else rise exception
        with sqlite3.connect("data.db") as db_connection:
            try:
                data_records.to_sql(
                    report_table, db_connection, if_exists="replace", index=False
                )
                print(
                    f"Data successfully saved to the table '{report_table}' in the database."
                )

            except Exception as e:
                print(
                    f"Failed to save data to the table '{report_table}' in the database. Error: {str(e)}"
                )
    except ConnectionError:
        # Handle the timeout exception
        print("Timeout: Failed to fetch data from the Socrata API.")
        print("Please try again later, or may try to use other IP adress.")
    except Exception as e:
        # Handle other unexpected exceptions
        print(f"Error occurred: {e}")


# Method for get unique market codes with data for at least the last 5 years
def find_common_codes(data_records, data_presence_years_back):
    current_year = dt.now().year
    reporting_years = range(current_year, current_year - data_presence_years_back, -1)

    common_codes = None
    for year in reporting_years:
        codes = data_records[
            data_records["yyyy_report_week_ww"].str[:4].astype(int) == year
        ]["cftc_contract_market_code"].unique()
        if common_codes is None:
            common_codes = set(codes)
        else:
            common_codes &= set(codes)

    return common_codes


if __name__ == "__main__":
    # print the available reports
    keys = REPORTS.keys()
    for index, key in enumerate(keys, start=1):
        print(f"{index}. {key}")

    # get the report number to fetch or use 'all' to fetch all
    user_input = input("Enter the report number (1-6) or 'all' to fetch all reports: ")

    # fetch the report logic
    if user_input == "all":
        fetch_all_reports()
    elif user_input.isdigit() and 1 <= int(user_input) <= 6:
        selected_report = list(REPORTS.keys())[int(user_input) - 1]
        fetch_single_report(selected_report)
    else:
        print("Invalid choice. Please enter 'all' or a number from 1 to 6.")
