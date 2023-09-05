import pandas as pd
from sodapy import Socrata
from reports_cols import (
    report_api_cols,
    main_api_cols,
    root_cols,
)
import sqlite3
from datetime import datetime as dt

REPORTS = {
    "Legacy - Futures Only": "6dca-aqww",
    "Legacy - Combined": "jun7-fc8e",
    "Disaggregated - Futures Only": "72hh-3qpy",
    "Disaggregated - Combined": "kh3c-gbw2",
    "TFF - Futures Only": "gpe5-46if",
    "TFF - Combined": "yw9f-hn96",
}


# Function to fetch data
def fetch_single_report(report_name):
    def find_common_codes(data_records, years_back):
        current_year = dt.now().year
        reporting_years = list(range(current_year, current_year - years_back, -1))
        # Get unique market codes with data for at least the last 5 years
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

    socrata_client = Socrata(
        "publicreporting.cftc.gov",
        None
        # Include your app token here
    )

    # Select the specific columns you want to fetch from the API
    selected_columns = main_api_cols + report_api_cols[report_name.split()[0].lower()]

    # Create a comma-separated list of selected columns for the API query
    selected_columns_query = ",".join(selected_columns)

    # Fetch data from the Socrata API for the specified reporting year range and convert to a pandas DataFrame
    data_records = pd.DataFrame.from_records(
        socrata_client.get(
            REPORTS[report_name],
            select=selected_columns_query,
            limit=9999999,
        )
    )

    print(f"Number of records fetched: {data_records.shape[0]}")

    codes_CFTC = find_common_codes(data_records, 6)
    data_records = data_records[
        data_records["cftc_contract_market_code"].isin(codes_CFTC)
    ]

    # Convert column names to lowercase, remove the "_all" suffix, and replace "__" with "_"
    data_records.columns = [
        col.lower().replace("_all", "").replace("__", "_")
        for col in data_records.columns
    ]

    # Print the number of records to be saved
    print(
        f"After filtering for data spanning over three years, the number of records to be saved is: {data_records.shape[0]}"
    )
    df_1 = data_records.iloc[:, :6]
    df_2 = data_records.iloc[:, 6:].apply(pd.to_numeric, errors="coerce")
    data_records = pd.concat([df_1, df_2], axis=1)
    for root in root_cols[report_name.split()[0].lower()]:
        print("Calculating net data for: " + root)
        data_records[f"{root}_net"] = data_records.apply(
            lambda row: row[f"{root}_long"] - row[f"{root}_short"], axis=1
        )
    # Replace NaN values with None
    data_records = data_records.where(pd.notna(data_records), None)

    # Create a table name for the SQLite database
    table_name = "report_" + "_".join(report_name.replace("-", "").split()).lower()

    # Print the table name being used for the database
    print(f"Table name for the database: {table_name}")

    # Save data to the SQLite database
    with sqlite3.connect("data.db") as db_connection:
        data_records.to_sql(table_name, db_connection, if_exists="replace", index=False)

    print(f"Data successfully saved to the table '{table_name}' in the database.")


# all report saving
def fetch_all_reports():
    for report_name in REPORTS:
        fetch_single_report(report_name)


if __name__ == "__main__":
    fetch_single_report("Supplemental - CIT")
    # fetch_all_reports()
