import pandas as pd
import requests
from sodapy import Socrata
import urllib3
from reports_cols import (
    report_api_cols,
    main_api_cols,
    root_cols,
)
import sqlite3
from datetime import datetime as dt
import time

# Define the number of years to look back for code availability
YEARS_BACK_FOR_CODES_AVABILITY = 3

# Dictionary mapping report names to their respective Socrata API codes
REPORTS_TABLE = {
    "report_legacy_futures_only": "6dca-aqww",
    "report_legacy_combined": "jun7-fc8e",
    "report_disaggregated_futures_only": "72hh-3qpy",
    "report_disaggregated_combined": "kh3c-gbw2",
    "report_tff_futures_only": "gpe5-46if",
    "report_tff_combined": "yw9f-hn96",
}

# Dictionary mapping human-readable report names to their respective Socrata API codes
REPORTS = {
    "Legacy - Futures Only": "6dca-aqww",
    "Legacy - Combined": "jun7-fc8e",
    "Disaggregated - Futures Only": "72hh-3qpy",
    "Disaggregated - Combined": "kh3c-gbw2",
    "TFF - Futures Only": "gpe5-46if",
    "TFF - Combined": "yw9f-hn96",
}

def get_socrata_api_data(report_code, selected_columns, last_week=""):
    """
    Fetch data from Socrata API and return as a pandas DataFrame.
    
    Args:
        report_code (str): The code of the report to fetch data from.
        selected_columns (str): Comma-separated string of column names to retrieve.
        last_week (str): Filter data to include records newer than this week.
    
    Returns:
        pd.DataFrame: Data fetched from the Socrata API.
    """
    data_records = None
    socrata_client = Socrata("publicreporting.cftc.gov", None)
    max_attempts = 2
    retry_delay_seconds = 3
    
    # Retry mechanism for API requests
    for attempt in range(1, max_attempts + 1):
        try:
            print("Making connection to Socrata API...")
            data_records = pd.DataFrame.from_records(
                socrata_client.get(
                    report_code,
                    select=selected_columns,
                    where=f"yyyy_report_week_ww > '{last_week}'",
                    limit=999999,
                )
            )
            # Break loop on successful attempt
            break
        except requests.exceptions.RequestException:
            print("Timeout: Read timed out...")
            break
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_attempts:
                print(f"Retrying in {retry_delay_seconds} seconds...")
                time.sleep(retry_delay_seconds)
            else:
                print("Max attempts reached. Cannot connect to Socrata API.")
                return data_records

    return data_records

def fetch_all_reports():
    """
    Fetch all reports listed in the REPORTS dictionary.
    """
    for report_name in REPORTS:
        fetch_single_report(report_name)

def fetch_new_all(reports_list):
    """
    Fetch new data for a list of reports, handling single tuples and lists.
    
    Args:
        reports_list (list or tuple): List of tuples containing report names and weeks.
    """
    # Convert single tuple to list if necessary
    if isinstance(reports_list, tuple):
        reports_list = [reports_list]

    for report in reports_list:
        fetch_new_report(report)

def fetch_new_report(report_table_name_and_week):
    """
    Fetch and process new report data, and save to SQLite database.
    
    Args:
        report_table_name_and_week (tuple): Contains report table name and last week for filtering.
    """
    report_table_name = report_table_name_and_week[0]
    report_last_week = report_table_name_and_week[1]
    report_root_name = report_table_name.split("_")[1]

    # Create a comma-separated list of selected columns for the API query
    selected_columns = ",".join(main_api_cols + report_api_cols.get(report_root_name, []))

    data_records = get_socrata_api_data(
        REPORTS_TABLE[report_table_name], selected_columns, report_last_week
    )
    
    if data_records is not None and not data_records.empty:
        print("New data found...")
        print(f"Number of records fetched: {data_records.shape[0]}")

        with sqlite3.connect("data.db") as db_connection:
            # Fetch CFTC codes for filtering
            cursor = db_connection.cursor()
            cursor.execute(
                f"SELECT cftc_contract_market_code FROM cftc_codes WHERE {report_table_name}=1"
            )
            codes_CFTC = cursor.fetchall()
            
            if codes_CFTC:
                codes_CFTC = [code[0] for code in codes_CFTC]
            else:
                print("No CFTC codes found for filtering.")
                return
        
        # Filtering data_records based on CFTC codes
        data_records = data_records[
            data_records["cftc_contract_market_code"].isin(codes_CFTC)
        ]
        print(f"Number of records to be saved: {data_records.shape[0]}")

        # Convert column names to lowercase and adjust naming conventions
        data_records.columns = [
            col.lower().replace("_all", "").replace("__", "_")
            for col in data_records.columns
        ]

        # Remove unnecessary columns if they exist
        columns_to_remove = [
            "market_and_exchange_names",
            "commodity",
            "commodity_subgroup_name",
            "contract_units",
        ]
        data_records = data_records.drop(
            [col for col in columns_to_remove if col in data_records.columns], 
            axis=1,
            errors='ignore'
        )

        # Convert columns to numeric types
        df_1 = data_records.iloc[:, :3]
        df_2 = data_records.iloc[:, 3:].apply(pd.to_numeric, errors="coerce")
        data_records = pd.concat([df_1, df_2], axis=1)

        # Calculate net positions for each root column
        for root in root_cols.get(report_root_name, []):
            print(f"Calculating net data for: {root}")
            long_col = f"{root}_long"
            short_col = f"{root}_short"
            if long_col in data_records.columns and short_col in data_records.columns:
                data_records[f"{root}_net"] = data_records[long_col].sub(
                    data_records[short_col]
                )
        
        # Replace NaN values with None for database compatibility
        data_records = data_records.where(pd.notna(data_records), None)

        # Save data to the SQLite database
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

def fetch_single_report(report_name):
    """
    Fetch and process a single report by its name, and save to SQLite database.
    
    Args:
        report_name (str): The name of the report to fetch.
    """
    report_main = report_name.split()[0].lower()

    # Create a comma-separated list of selected columns for the API query
    selected_columns_query = ",".join(main_api_cols + report_api_cols[report_main])

    data_records = get_socrata_api_data(REPORTS[report_name], selected_columns_query)

    if data_records is not None and not data_records.empty:
        # Find unique market codes spanning over the last specified years
        codes_CFTC = find_common_codes(data_records, YEARS_BACK_FOR_CODES_AVABILITY)

        # Filter for data with codes spanning the last years
        data_records = data_records[
            data_records["cftc_contract_market_code"].isin(codes_CFTC)
        ]

        print(
            f"After filtering for data spanning over {YEARS_BACK_FOR_CODES_AVABILITY} years, the number of records to be saved is: {data_records.shape[0]}"
        )

        # Convert column names to lowercase and adjust naming conventions
        data_records.columns = [
            col.lower().replace("_all", "").replace("__", "_")
            for col in data_records.columns
        ]

        # Create a table name based on the report name
        report_table = "report_" + "_".join(
            report_name.replace("- ", "").lower().split()
        )

        # Create 'cftc_codes' table if it doesn't exist
        with sqlite3.connect("data.db") as db_connection:
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

            # Find new unique CFTC Contract Market Codes not existing in the database
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

        # Update 'cftc_codes' table to mark which reports contain each code
        with sqlite3.connect("data.db") as db_connection:
            codes_CFTC = [str(code) for code in codes_CFTC]
            query = f"UPDATE cftc_codes SET {report_table} = True WHERE cftc_contract_market_code IN ({', '.join('?' for _ in codes_CFTC)})"
            db_connection.execute(query, codes_CFTC)

        # Drop unnecessary columns for final processing
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

        # Convert data values to numeric types for proper saving
        df_1 = data_records.iloc[:, :3]
        df_2 = data_records.iloc[:, 3:].apply(pd.to_numeric, errors="coerce")
        data_records = pd.concat([df_1, df_2], axis=1)

        # Calculate net positions for each root column
        for root in root_cols[report_main]:
            print(f"Calculating net data for: {root}")
            data_records[f"{root}_net"] = data_records.apply(
                lambda row: row[f"{root}_long"] - row[f"{root}_short"], axis=1
            )

        # Replace NaN values with None for database compatibility
        data_records = data_records.where(pd.notna(data_records), None)

        # Save data to the SQLite database
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
    else:
        print("No new report found.")

def find_common_codes(data_records, years_back_codes_avability):
    """
    Find unique market codes with data available for at least the number of years specified.
    
    Args:
        data_records (pd.DataFrame): DataFrame containing the data records.
        years_back_codes_avability (int): Number of years to look back for code availability.
    
    Returns:
        set: Set of CFTC contract market codes available for the specified number of years.
    """
    current_year = dt.now().year
    reporting_years = range(current_year, current_year - years_back_codes_avability, -1)

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
    # Print the available reports with their indices
    keys = REPORTS.keys()
    for index, key in enumerate(keys, start=1):
        print(f"{index}. {key}")

    # Get user input to fetch specific report or all reports
    user_input = input("Enter the report number (1-6) or 'all' to fetch all reports: ")

    # Fetch the report based on user input
    if user_input == "all":
        fetch_all_reports()
    elif user_input.isdigit() and 1 <= int(user_input) <= 6:
        selected_report = list(REPORTS.keys())[int(user_input) - 1]
        fetch_single_report(selected_report)
    else:
        print("Invalid choice. Please enter 'all' or a number from 1 to 6.")
