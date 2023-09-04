# Function to map column names based on a report
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from utils import *
from ticker_finder import *
import sqlite3
import pandas as pd
import yfinance as yf
from reports_cols import root_cols_desc, root_cols


def map_column_name(report, column_name):
    category = root_cols_desc[report]
    name = ""
    print("column name: ", column_name)
    column_name = column_name.replace("pct_of_oi_", "").replace("_positions", "")
    if column_name.endswith("_net"):
        sufix = " Net"
        column_name = column_name.replace("_net", "")
    elif column_name.endswith("_short"):
        sufix = " Short"
        column_name = column_name.replace("_short", "")
    elif column_name.endswith("_long"):
        print("Detected suffix: _long")
        sufix = " Long"
        column_name = column_name.replace("_long", "")
    print(column_name)
    # Zaktualizowano poniższą linię, aby pobierać odpowiedni opis z kategorii
    name += category[column_name] + sufix
    return name


# Function to retrieve data from a database
def get_data(report_type, selected_market_commodity, years):
    conn = sqlite3.connect("data.db")
    report = report_type.split("_")[1]
    roots = root_cols[report]
    cols = (
        [f"{item}_net" for item in roots]
        + [f"{item}_long" for item in roots]
        + [f"{item}_short" for item in roots]
    )
    column_str = ", ".join(list(cols))
    query = f"""
    SELECT report_date_as_yyyy_mm_dd, {column_str}
    FROM {report_type}
    WHERE market_and_exchange_names = ?
    AND report_date_as_yyyy_mm_dd BETWEEN ? AND ?
    ORDER BY 1 ASC
    """
    params = (selected_market_commodity, f"{years[0]}-01-01", f"{years[1]}-12-31")
    df_data = pd.read_sql(query, conn, params=params)
    df_data.rename(columns={"report_date_as_yyyy_mm_dd": "Date"}, inplace=True)
    df_data.set_index("Date", inplace=True)
    df_data.index = pd.to_datetime(df_data.index)
    conn.close()
    return df_data


# Function to retrieve price data
def get_price_data(ticker, year):
    start_date = f"{year[0]}-01-01" if year != [0, 0] else None
    end_date = f"{year[1]}-12-31" if year != [0, 0] else None
    return yf.download(ticker, start_date, end_date, "1wk")["Close"].to_frame()


# Function to create a figure for graphs
def create_figure(df, name, columns_selected=False, price_chart=True, price_name=""):
    if df.columns[-1].startswith("pct"):
        name = "[%] PERCENTAGE CHART OF " + name
    elif df.columns[-1] == "Close":
        name = "[$] PRICE CHART OF " + price_name
    else:
        name = "POSITIONS CHART OF " + name

    fig = {
        "data": [],
        "layout": {
            "title": {
                "text": name,
            },
            "legend": {"orientation": "h", "y": 1.15},
        },
    }

    for col in df.columns:
        if col == "Close" and price_chart:
            print("Close column in data..")
            print("Adding Price Chart")
            fig["data"].append(
                {
                    "x": df.index,
                    "y": df[col],
                    "type": "line",
                    "name": f"PRICE of {price_name} [$]",
                    "yaxis": "y2",
                }
            )
            fig["layout"]["yaxis2"] = {
                "overlaying": "y",
                "side": "right",
                "title": "PRICE [$]",
                "showgrid": False,
            }

        elif col in columns_selected:
            print(f"Adding Line for {col}")
            fig["data"].append(
                {
                    "x": df.index,
                    "y": df[col],
                    "type": "line",
                    "name": col,
                    "line": {"width": 1},
                    "yaxis": "y1",
                }
            )
    return fig


def make_graphs_card(
    yahoo_tickers,
    report_type,
    market_commodity,
    positions,
    years,
    options,
    ticker,
    add_price,
):
    # Initialize data and figure variables
    df_price, df_positions, df_percentages = (
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
    )
    fig_price, fig_positions, fig_percentages = {}, {}, {}

    # Extract the report type
    report = report_type.split("_")[1]

    # Initialize card_percentage as an empty list
    card_percentage = []

    # Retrieve market commodity data if selected
    if market_commodity:
        print("market_commodity ", market_commodity)
        df_data = get_data(report_type, market_commodity, years)

        df_percentages = df_data.filter(regex=r"^pct_of_oi")
        df_positions = df_data.drop(columns=df_percentages.columns)

    # Retrieve price data if a ticker is selected
    if ticker:
        price_name = yahoo_tickers[ticker].upper()
        df_price = get_price_data(ticker, years)
        fig_price = create_figure(
            df_price, ticker, price_chart=True, price_name=price_name
        )

        # If market_commodity is selected, perform additional operations
        if market_commodity:
            df_price_weekly = df_price.resample("W").mean()
            df_positions = pd.concat([df_price_weekly, df_positions], axis=1).fillna(
                method="ffill"
            )
            df_percentages = pd.concat(
                [df_price_weekly, df_percentages], axis=1
            ).fillna(method="ffill")

            # df_positions = df_positions.interpolate() instead of ffill

            correlations_positions = df_positions.corr()["Close"].drop("Close")
            sorted_correlations_positions = correlations_positions.abs().sort_values(
                ascending=False
            )
            correlation_text_positions = get_correlation_text(
                report, sorted_correlations_positions
            )

            correlations_percentage = df_percentages.corr()["Close"].drop("Close")
            sorted_correlations_percentage = correlations_percentage.abs().sort_values(
                ascending=False
            )
            correlation_text_percentage = get_correlation_text(
                report, sorted_correlations_percentage
            )

            # Create card_percentage with correlation information
            card_percentage = create_correlation_card(
                price_name, correlation_text_positions, correlation_text_percentage
            )

    # If market_commodity and positions are selected, process and create figures
    if market_commodity and positions and options:
        percentage_cols, positions_cols = [], []

        percentage_cols = [
            "pct_of_oi_" + x + "_" + y for x in positions for y in options
        ]

        positions_cols = [x + "_positions_" + y for x in positions for y in options]
        if add_price:
            fig_positions = create_figure(
                df_positions,
                market_commodity,
                positions_cols,
                True,
                price_name,
            )
            fig_percentages = create_figure(
                df_percentages,
                market_commodity,
                percentage_cols,
                True,
                price_name,
            )
        else:
            fig_positions = create_figure(
                df_positions,
                market_commodity,
                positions_cols,
                False,
            )

            fig_percentages = create_figure(
                df_percentages, market_commodity, percentage_cols, False
            )

    # Generate the formatted correlation text and return the figures
    return fig_price, fig_positions, card_percentage, fig_percentages


# method to get correlation text
def get_correlation_text(report, correlations):
    return [
        html.P(
            f"{map_column_name(report, col)} {'positive: +' if correlations[col] >= 0 else 'negative: -'}{correlation:.2f}",
            style={"margin": "5px"},
        )
        for col, correlation in correlations.items()
    ]


# method to create a correlation card
def create_correlation_card(
    price_name, correlation_text_positions, correlation_text_percentage
):
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H4(
                        f"Pearson's correlations of {price_name.lower()} (contracts):"
                    ),
                    *correlation_text_positions,
                ]
            ),
            dbc.Col(
                [
                    html.H4(
                        f"Pearson's correlations percentage of {price_name.lower()} (percentages):"
                    ),
                    *correlation_text_percentage,
                ]
            ),
        ]
    )
