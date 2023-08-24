import pandas as pd
import sqlite3
from datetime import date
import json


def load_yahoo_tk_data():
    with open("yahoo_tk_futures.json") as f:
        yahoo_tk_data = json.load(f)
    return yahoo_tk_data


def get_reports_opts():
    with sqlite3.connect("data.db") as conn:
        query = (
            "SELECT name FROM sqlite_schema WHERE type='table' AND name like 'report_%'"
        )
        tables = pd.read_sql(query, conn)["name"]

    labels = [name.replace("report_", "").replace("_", " ").title() for name in tables]
    values = [name for name in tables]

    return [{"label": label, "value": value} for label, value in zip(labels, values)]


def get_commodities_opts(table):
    conn = sqlite3.connect("data.db")
    query_unique_commodities = f'SELECT DISTINCT commodity_name FROM {table} where yyyy_report_week_ww like "%{date.today().year}%" ORDER BY 1 ASC'
    unique_commodities = pd.read_sql(query_unique_commodities, conn)["commodity_name"]
    conn.close()
    dropdown_options = [
        {"label": commodity, "value": commodity} for commodity in unique_commodities
    ]

    return dropdown_options


def get_market_opts(selected_commodity, report_table):
    # Pobranie unikalnych towarów z bazy danych do listy wyboru
    conn = sqlite3.connect("data.db")
    query_unique_commodities = f'SELECT DISTINCT market_and_exchange_names FROM {report_table} where yyyy_report_week_ww like "%{date.today().year}%" AND commodity_name="{selected_commodity}" ORDER BY 1 ASC'
    unique_commodities = pd.read_sql(query_unique_commodities, conn)[
        "market_and_exchange_names"
    ]
    conn.close()

    dropdown_options = [
        {"label": commodity, "value": commodity} for commodity in unique_commodities
    ]

    return dropdown_options


def get_slider_range_dates(comodity):
    conn = sqlite3.connect("data.db")
    query_min_max_dates = f"SELECT MIN(report_date_as_yyyy_mm_dd) as min_date, MAX(report_date_as_yyyy_mm_dd) as max_date FROM report_legacy_futures_only where market_and_exchange_names = '{comodity}' "
    min_max_dates = pd.read_sql(query_min_max_dates, conn)
    min_date, max_date = (
        int(min_max_dates["min_date"].iloc[0][:4]),
        int(min_max_dates["max_date"].iloc[0][:4]),
    )

    conn.close()
    return min_date, max_date


def get_slider_opts(selected_commodity):
    min_date, max_date = get_slider_range_dates(selected_commodity)
    # Tworzymy znaczniki (marks) dla slidera
    marks = {year: str(year) for year in range(min_date, max_date + 1, 2)}
    # Zwracamy nowy zakres slidera oraz znaczniki
    return min_date, max_date, [min_date, max_date], marks
