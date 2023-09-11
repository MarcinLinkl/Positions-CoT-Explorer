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
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MAX(yyyy_report_week_ww) FROM report_legacy_futures_only;"
        )
        latest_week = cursor.fetchone()[0]
    except sqlite3.Error as e:
        print("Error when checking for new reports:", e)
    if latest_week is not None:
        current_week = datetime.date.today().strftime("%Y Report Week %W")
        if latest_week < current_week:
            print(f"latest report: {latest_week}, current week: {current_week}")
            fetch_new_all(latest_week)
    conn.close()


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


def get_market_opts(selected_commodity, report):
    # Pobranie unikalnych towarów z bazy danych do listy wyboru
    conn = sqlite3.connect("data.db")
    query_unique_commodities = f'SELECT DISTINCT market_and_exchange_names,cftc_contract_market_code,contract_units FROM cftc_codes where {report}=1 and commodity_subgroup_name="{selected_commodity}" ORDER BY 1 ASC'
    unique_commodities_df = pd.read_sql(query_unique_commodities, conn)
    conn.close()
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
        for name_market, cftc_code, contract_units in zip(
            unique_commodities_df["market_and_exchange_names"],
            unique_commodities_df["cftc_contract_market_code"],
            unique_commodities_df["contract_units"],
        )
    ]

    return dropdown_options


def get_slider_range_dates(selected_cftc_code):
    cftc_code = json.loads(selected_cftc_code)["cftc_code"]
    conn = sqlite3.connect("data.db")
    query_min_max_dates = f"SELECT MIN(report_date_as_yyyy_mm_dd) as min_date, MAX(report_date_as_yyyy_mm_dd) as max_date FROM report_legacy_futures_only where cftc_contract_market_code = {cftc_code} "
    min_max_dates = pd.read_sql(query_min_max_dates, conn)
    min_date, max_date = (
        int(min_max_dates["min_date"].iloc[0][:4]),
        int(min_max_dates["max_date"].iloc[0][:4]),
    )

    conn.close()
    return min_date, max_date


def get_slider_opts(selected_cftc_code):
    min_date, max_date = get_slider_range_dates(selected_cftc_code)
    # Tworzymy znaczniki (marks) dla slidera
    if (max_date - min_date) < 6:
        marks_step = 1
    else:
        marks_step = 2
    marks = {year: str(year) for year in range(min_date, max_date + 1, marks_step)}
    # Zwracamy nowy zakres slidera oraz znaczniki
    return min_date, max_date, [min_date, max_date], marks
