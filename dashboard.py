import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from utils import *
from ticker_finder import *
import sqlite3
import pandas as pd
from reports_definitions import positions_by_report, reports_cols

yahoo_tk_data = load_yahoo_tk_data()


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Select CFTC report:"),
                        dcc.Dropdown(
                            id="report-dropdown",
                            options=get_reports_opts(),
                            value="report_legacy_futures_only",
                            placeholder="Select a report",
                            optionHeight=50,
                            className="dash-dropdown",
                            style={
                                "borderRadius": "15px",
                            },
                        ),
                    ],
                    className="col-lg-6 col-12 my-2 text-center",
                ),
                dbc.Col(
                    [
                        dbc.Label("Select a commodity:"),
                        dcc.Dropdown(
                            id="commodities-dropdown",
                            placeholder="Select a commodity",
                            optionHeight=50,
                            className="dash-dropdown",
                            style={"borderRadius": "15px"},
                        ),
                    ],
                    className="col-lg-6 col-12 my-2 text-center",
                ),
                dbc.Col(
                    [
                        dbc.Label(
                            "Select a specific commodity market/commodity exchange name: "
                        ),
                        dcc.Dropdown(
                            id="market-and-exchange-names-dropdown",
                            placeholder="Select a market/exchange",
                            optionHeight=50,
                            className="dash-dropdown",
                            style={"borderRadius": "15px"},
                        ),
                    ],
                    className="col-12 my-2 text-center",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Select min max dates:"),
                        dcc.RangeSlider(
                            id="year-slider",
                            step=1,
                            className="col-12 px-10 custom-range-slider",
                        ),
                    ],
                    className="px-2 text-center",
                ),
            ],
            className="p-2",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Select a price chart: ", id="price-chart-label"),
                        dcc.Dropdown(
                            id="chart-price-dropdown",
                            options=[
                                {"label": f"Price of {i.lower()}", "value": j}
                                for i, j in yahoo_tk_data.items()
                            ],
                            placeholder="Select price",
                            optionHeight=50,
                            className="dash-bootstrap",
                            style={"borderRadius": "15px"},
                        ),
                    ],
                    className="col-lg-6 col-12 my-2 text-center",
                ),
                dbc.Col(
                    [
                        dbc.Label("Position types : "),
                        dcc.Dropdown(
                            id="position-type",
                            multi=True,
                            placeholder="Select a position type",
                            className="dash-bootstrap",
                            style={
                                "borderRadius": "15px",
                                # "text-align": "left"
                            },
                        ),
                    ],
                    className="col-lg-6 col-12 my-2 text-center",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Checklist(
                        id="display-chart",
                        options=[
                            {
                                "label": "Display additional price",
                                "value": True,
                            },
                        ],
                        value=[True],
                        inline=True,
                        labelStyle={
                            "display": "inline-block",
                            "margin": "0 0 0 15px",
                            "text-align": "center",
                            "font-size": "18px",
                        },
                        switch=True,
                        className="text-center",
                    ),
                    className="col-lg-3 col-6 my-2",
                ),
                dbc.Col(
                    dbc.Checklist(
                        id="add-price-line",
                        options=[
                            {
                                "label": "Add price line",
                                "value": True,
                            },
                        ],
                        value=False,
                        inline=True,
                        labelStyle={
                            "display": "inline-block",
                            "margin": "0 0 0 15px",
                            "text-align": "center",
                            "font-size": "18px",
                        },
                        switch=True,
                        className="text-center",
                    ),
                    className="col-lg-3 col-6 my-2",
                ),
                dbc.Col(
                    dbc.Button(
                        "Show correlations",
                        id="submit-button",
                        color="success",
                        # className="custom-button",
                        # className="col-2 text-center",  # zmieniono na col-2
                        style={
                            "display": "inline-block",
                            "max-height": "30px",
                            "border-radius": "15px",
                            "text-align": "center",
                            "margin": "0",
                            "padding": "0",
                            "width": "calc(50%)",
                        },
                    ),
                    className="col-lg-3 col-6 my-2 text-center",
                ),
                dbc.Col(
                    dbc.Checklist(
                        id="show-option",
                        options=[
                            {"label": i.capitalize(), "value": i}
                            for i in ["net", "long", "short"]
                        ],
                        value=["net"],
                        inline=True,
                        labelStyle={
                            "display": "inline-block",
                            "margin": "0 0 0 15px",
                            "font-weight": "bold",
                            "font-size": "18px",
                        },
                        className="text-center",
                    ),
                    className="col-lg-3 col-6 my-2",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="price-graph",
                        className="col-12 my-2",
                    ),
                    className="col-12",
                ),
                dbc.Col(
                    dcc.Graph(
                        id="commodity-graph",
                        className="col-12 my-2",
                    ),
                    className="col-12",
                ),
            ],
            className="p-2",
        ),
    ],
    fluid=True,
)


@app.callback(
    Output("position-type", "options"),
    Output("position-type", "value"),
    Input("report-dropdown", "value"),
)
def update_position_types(report):
    if report is None:
        return [], []
    return get_positions_types_opts(report)


def get_positions_types_opts(report):
    selected_report = rep_prefix(report)
    # report_legacy_futures_only
    return (
        [
            {"label": j, "value": i}
            for i, j in positions_by_report[selected_report].items()
        ],
        [list(positions_by_report[selected_report].keys())[0]],
    )


@app.callback(
    Output("commodities-dropdown", "options"), Input("report-dropdown", "value")
)
def update_commodities_dropdown(report):
    if report is None:
        return []
    return get_commodities_opts(report)


@app.callback(
    Output("market-and-exchange-names-dropdown", "options"),
    Input("commodities-dropdown", "value"),
    Input("report-dropdown", "value"),
)
def update_market_dropdown(selected_commodity, selected_report):
    if selected_commodity is None or selected_report is None:
        return []
    return get_market_opts(selected_commodity, selected_report)


@app.callback(
    Output("price-chart-label", "children"),
    Output("chart-price-dropdown", "value"),
    Output("year-slider", "min"),
    Output("year-slider", "max"),
    Output("year-slider", "value"),
    Output("year-slider", "marks"),
    Input("market-and-exchange-names-dropdown", "value"),
)
def update_year_slider_and_price_dropdown_value(selected):
    """
    Update the year slider and price dropdown value based on the selected market and exchange names.

    Parameters:
    selected (any): The selected market and exchange names.

    Returns:
    price_chart_label (str): The label for the price chart.
    ticker_dropdown (any): The value of the ticker dropdown.
    min_y (int): The minimum value of the year slider.
    max_y (int): The maximum value of the year slider.
    values (list): The values of the year slider.
    marks (dict): The marks for the year slider.
    """
    if selected is None:
        return "Select a price chart:", None, 0, 0, [0, 0], {}

    ticker_dropdown = find_similar_ticker(selected, yahoo_tk_data)
    price_chart_label = (
        "Price chart not found; may need to select one manually:"
        if ticker_dropdown is None
        else f"Price chart found: {ticker_dropdown}, you can adjust manually if needed"
    )

    min_y, max_y, values, marks = get_slider_opts(selected)
    # Dodaj opis w zależności od znalezionego tickera

    return price_chart_label, ticker_dropdown, min_y, max_y, values, marks


@app.callback(
    Output("price-graph", "style"),
    Input("display-chart", "value"),
)
def toggle_price_graph_visibility(chart_together_value):
    """
    Toggles the visibility of the price graph based on the value of the "display-chart" input.

    Parameters:
        chart_together_value (list): A list containing a single boolean value indicating whether the price graph should be displayed together with the chart.

    Returns:
        dict: A dictionary representing the style of the "price-graph" output. If the value of "chart_toge  ther_value" is not [True], the style will be {"display": "none"}. Otherwise, an empty dictionary will be returned.
    """
    return {"display": "none"} if chart_together_value != [True] else {}


def rename_columns(df):
    print("rename columns")
    for column in df.columns:
        if column.endswith("short"):
            new_column = column.replace("short", "short_all")
            df.rename(columns={column: new_column}, inplace=True)
        elif column.endswith("long"):
            new_column = column.replace("long", "long_all")
            df.rename(columns={column: new_column}, inplace=True)
        elif column == "swap__positions_short_all":
            df.rename(columns={column: column.replace("__", "_")}, inplace=True)
    return df


def get_position_data(report_type, selected_market_commodity, years):
    columns = list(reports_cols[rep_prefix(report_type)]["positions"].keys())

    column_str = ", ".join(columns)
    query = f"""
    SELECT report_date_as_yyyy_mm_dd, {column_str}
    FROM {report_type}
    WHERE market_and_exchange_names = ?
    AND report_date_as_yyyy_mm_dd BETWEEN ? AND ?
    ORDER BY 1 ASC
    """
    print(query)
    conn = sqlite3.connect("data.db")
    params = (selected_market_commodity, f"{years[0]}-01-01", f"{years[1]}-12-31")

    df_data = pd.read_sql(query, conn, params=params)

    conn.close()

    print(df_data)

    df_data.rename(columns={"report_date_as_yyyy_mm_dd": "Date"}, inplace=True)
    df_data.set_index("Date", inplace=True)
    df_data.index = pd.to_datetime(df_data.index)
    df_data = rename_columns(df_data)

    pos_types = positions_by_report[rep_prefix(report_type)]
    for pos_type in pos_types:
        print("position: ", pos_type)
        df_data[f"{pos_type}_net_all"] = pd.to_numeric(
            df_data[f"{pos_type}_long_all"]
        ) - pd.to_numeric(df_data[f"{pos_type}_short_all"], errors="coerce")
    print("done... postions data fetche from ", report_type)
    return df_data


@app.callback(
    Output("price-graph", "figure"),
    Output("commodity-graph", "figure"),
    Input("report-dropdown", "value"),
    Input("market-and-exchange-names-dropdown", "value"),
    Input("position-type", "value"),
    Input("year-slider", "value"),
    Input("show-option", "value"),
    Input("chart-price-dropdown", "value"),
    Input("add-price-line", "value"),
)
def update_graphs_callback(
    report_type, market_commodity, positions, years, options, ticker, add_price
):
    df_price, df_positions, merged_df = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    fig_price, fig_positions = {}, {}
    if ticker:
        df_price = get_price_data(ticker, years)
        print(df_price.head())
        fig_price = create_figure_positions(df_price, ticker, positions, options)
    if market_commodity:
        df_positions = get_position_data(report_type, market_commodity, years)

    if ticker and market_commodity:
        df_price_weekly = df_price.resample("W").mean()

        merged_df = pd.concat([df_price_weekly, df_positions], axis=1)
        # merged_df = merged_df.interpolate()
        merged_df = merged_df.fillna(method="ffill")
        print(merged_df)
        if positions and options:
            if add_price:
                fig_positions = create_figure_positions(
                    merged_df, market_commodity, positions, options
                )
            else:
                fig_positions = create_figure_positions(
                    df_positions, market_commodity, positions, options
                )

    return fig_price, fig_positions


def get_price_data(ticker, year):
    start_date = f"{year[0]}-01-01" if year != [0, 0] else None
    end_date = f"{year[1]}-12-31" if year != [0, 0] else None
    return yf.download(ticker, start_date, end_date, "1wk")["Close"].to_frame()


def create_figure_positions(df, name, positions, options):
    fig = {
        "data": [],
        "layout": {
            "margin": {"l": 30, "r": 30, "t": 30, "b": 30},  # Marginesy wokół wykresu
            "title": f"{name}",  # Tytuł wykresu
            "yaxis": {"title": "Pozycje", "y": "-0.5"},  # Etykieta osi Y
            "legend": {"orientation": "h", "y": 1},  # Legenda wykresu (poziomo)
            # "legend": {"orientation": "v", "y": 1},  # Legenda wykresu (pionowo)
        },
    }

    cols_selected = [f"{pos}_{opt}_all" for pos in positions for opt in options]
    print(cols_selected)
    print([col for col in df.columns])
    for col in df.columns:
        if col == "Close":
            fig["data"].append(
                {
                    "x": df.index,
                    "y": df[col],
                    "type": "line",
                    "name": "Price $",
                    "yaxis": "y2",  # Dodanie drugiej osi y dla ceny towaru
                    # "line": {"width": 1, "color": "firebrick", "dash": "line"},
                }
            )
            fig["layout"]["yaxis2"] = {
                "overlaying": "y",  # Nakładająca się na pierwszą oś y
                "side": "right",  # Po prawej stronie
                "title": "Price",  # Tytuł dla drugiej osi y
                "showgrid": False,  # Wyłączenie siatki dla drugiej osi y
            }
        elif col in cols_selected:
            print(col, "True")
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

    # fig["layout"]["xaxis"] = {
    #     "range": [df.index[0], df.index[-1]],
    # }
    return fig


if __name__ == "__main__":
    app.run(debug=True, port=2077)
