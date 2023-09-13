import datetime
import pandas as pd
import sqlite3
import json
from bidict import bidict
import json
from fetch_data import fetch_new_all


def load_yahoo_tk_data():
    with open("yahoo_tk_futures.json") as f:
        yahoo_tk_data = json.load(f)
    return bidict(yahoo_tk_data)


def check_for_new_records():
    current_date = datetime.date.today()
    check_latest_weeks_table = []
    print("Current week:", current_date.strftime("%Y Week %W"))
    try:
        with sqlite3.connect("data.db") as conn:
            cursor = conn.cursor()
            query = "SELECT name FROM sqlite_schema WHERE type='table' AND name LIKE 'report_%'"
            cursor.execute(query)
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                query_max_week = f"SELECT MAX(yyyy_report_week_ww) as week_report, MAX(report_date_as_yyyy_mm_dd) as report_date FROM {table_name}"
                cursor.execute(query_max_week)
                latest_week, latest_report_date = cursor.fetchone()
                if latest_report_date:
                    latest_report_date = datetime.datetime.strptime(
                        latest_report_date, "%Y-%m-%dT%H:%M:%S.%f"
                    ).date()
                    days_diff = (current_date - latest_report_date).days
                    if days_diff >= 10:
                        print(
                            f"{table_name.replace('_', ' ').title()}, latest Week: {latest_week}. Checked for new one."
                        )
                        check_latest_weeks_table.append((table_name, latest_week))
                    else:
                        print(
                            f"{table_name.replace('_', ' ').title()}, latest Week: {latest_week}."
                        )
    except sqlite3.Error as e:
        print("Error when checking for new reports:", e)
        return None
    if check_latest_weeks_table:
        fetch_new_all(check_latest_weeks_table)
    else:
        print("Data up to date.")


def get_reports_opts():
    with sqlite3.connect("data.db") as conn:
        query = "SELECT name FROM sqlite_schema WHERE type='table' AND name like 'report_%' order by 1 asc"
        tables = pd.read_sql(query, conn)["name"]

    labels = [name.replace("report_", "").replace("_", " ").title() for name in tables]
    values = [name for name in tables]

    return [{"label": label, "value": value} for label, value in zip(labels, values)]


def get_commodities_subgroup_opts(report):
    conn = sqlite3.connect("data.db")
    query_unique_commodities = f"SELECT DISTINCT commodity_subgroup_name FROM cftc_codes where {report} = 1 ORDER BY 1 ASC"
    unique_commodities = pd.read_sql(query_unique_commodities, conn)[
        "commodity_subgroup_name"
    ]

    conn.close()
    dropdown_options = [
        {"label": commodity, "value": commodity} for commodity in unique_commodities
    ]

    return dropdown_options


def get_market_opts(report, selected_commodity=None):
    query_and_where = (
        f"and commodity_subgroup_name = '{selected_commodity}'"
        if selected_commodity
        else ""
    )

    with sqlite3.connect("data.db") as conn:
        query_unique_commodities = f"""
            SELECT DISTINCT market_and_exchange_names, cftc_contract_market_code, contract_units 
            FROM cftc_codes 
            WHERE {report} = 1 {query_and_where}
            ORDER BY 1 ASC
        """
        unique_commodities_df = pd.read_sql_query(query_unique_commodities, conn)

    unique_commodities_df.drop_duplicates(
        subset="cftc_contract_market_code", inplace=True
    )

    dropdown_options = [
        {
            "label": name_market,
            "value": json.dumps(
                {
                    "cftc_code": cftc_code,
                    "name_market": name_market,
                    "units": contract_units,
                }
            ),
        }
        for name_market, cftc_code, contract_units in unique_commodities_df[
            ["market_and_exchange_names", "cftc_contract_market_code", "contract_units"]
        ].itertuples(index=False)
    ]

    return dropdown_options


def get_slider_range_dates(selected_cftc_code, report):
    cftc_code = json.loads(selected_cftc_code)["cftc_code"]
    conn = sqlite3.connect("data.db")
    query_min_max_dates = f"SELECT MIN(report_date_as_yyyy_mm_dd) as min_date, MAX(report_date_as_yyyy_mm_dd) as max_date FROM {report} where cftc_contract_market_code = '{cftc_code}' "
    min_max_dates = pd.read_sql(query_min_max_dates, conn)
    min_date = min_max_dates["min_date"].iloc[0]
    max_date = min_max_dates["max_date"].iloc[0]
    conn.close()
    if min_date is not None and max_date is not None:
        min_date = int(min_date[:4])
        max_date = int(max_date[:4])
    else:
        min_date = 0
        max_date = 0
        # Handle the case where no data was found, e.g., by returning some default values.
    return min_date, max_date


def get_slider_opts(selected_cftc_code, report):
    min_date, max_date = get_slider_range_dates(selected_cftc_code, report)
    # we maake mark step 2 if min_date - max_date < 6
    if (max_date - min_date) < 6:
        marks_step = 1
    else:
        marks_step = 2
    marks = {year: str(year) for year in range(min_date, max_date + 1, marks_step)}
    return min_date, max_date, [min_date, max_date], marks
