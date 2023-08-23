import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from utils import *
from ticker_finder import *
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

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
                            options=get_chart_price_opts(yahoo_tk_data),
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
                            options=[
                                {"label": "Commercial", "value": "comm_positions"},
                                {
                                    "label": "Non-Commercial",
                                    "value": "noncomm_positions",
                                },
                                {
                                    "label": "Non-Reportable",
                                    "value": "nonrept_positions",
                                },
                                {
                                    "label": "Total Reportable",
                                    "value": "tot_rept_positions",
                                },
                            ],
                            value=["noncomm_positions"],
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
                            {"label": "Net", "value": "net"},
                            {"label": "Long", "value": "long"},
                            {"label": "Short", "value": "short"},
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
                    dcc.Graph(id="price-graph", className="col-12 my-2"),
                    className="col-12",
                ),
                dbc.Col(
                    dcc.Graph(id="commodity-graph", className="col-12 my-2"),
                    className="col-12",
                ),
            ],
            className="p-2",
        ),
    ],
    fluid=True,
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
        dict: A dictionary representing the style of the "price-graph" output. If the value of "chart_together_value" is not [True], the style will be {"display": "none"}. Otherwise, an empty dictionary will be returned.
    """
    return {"display": "none"} if chart_together_value != [True] else {}


def get_legacy_futures(selected_market_commodity, position_type, year):
    columns = ", ".join(
        [f"{pos_type}_long_all, {pos_type}_short_all" for pos_type in position_type]
    ).replace("tot_rept_positions_short_all", "tot_rept_positions_short")
    query = f"""
    SELECT report_date_as_yyyy_mm_dd, {columns}
    FROM report_legacy_futures_only
    WHERE market_and_exchange_names = ?
    AND report_date_as_yyyy_mm_dd BETWEEN ? AND ?
    ORDER BY 1 ASC
    """
    conn = sqlite3.connect("data.db")
    params = (selected_market_commodity, f"{year[0]}-01-01", f"{year[1]}-12-31")
    df_data = pd.read_sql(query, conn, params=params)
    conn.close()

    df_data = df_data.rename(
        columns={"tot_rept_positions_short": "tot_rept_positions_short_all"}
    )
    df_data.rename(columns={"report_date_as_yyyy_mm_dd": "Date"}, inplace=True)
    df_data.set_index("Date", inplace=True)
    df_data.index = pd.to_datetime(df_data.index)
    for pos_type in position_type:
        df_data[f"{pos_type}_net"] = pd.to_numeric(
            df_data[f"{pos_type}_long_all"]
        ) - pd.to_numeric(df_data[f"{pos_type}_short_all"], errors="coerce")
    return df_data


def get_position_data(report_type, selected_market_commodity, position_type, year):
    if report_type == "report_legacy_futures_only":
        return get_legacy_futures(selected_market_commodity, position_type, year)


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
    report_type, selected_market_commodity, positions, year, options, ticker, add_price
):
    fig_price, fig_positions = {}, {}
    if ticker:
        df_price = get_price_data(ticker, year)
        fig_price = create_figure(df_price, ticker)

    if selected_market_commodity and positions and options:
        df_positions = get_position_data(
            report_type, selected_market_commodity, positions, year
        )
        fig_positions = create_figure(df_positions, selected_market_commodity)

        if add_price and ticker:
            fig_positions = add_price_chart(fig_positions, df_price, ticker)

    return fig_price, fig_positions


def get_price_data(ticker, year):
    start_date = f"{year[0]}-01-01" if year != [0, 0] else None
    end_date = f"{year[1]}-12-31" if year != [0, 0] else None
    return yf.download(ticker, start_date, end_date, "1wk")["Close"].to_frame()


def create_figure(df_price, ticker):
    data = []
    for col in df_price.columns:
        trace = go.Scatter(x=df_price.index, y=df_price[col], mode="lines", name=col)
        data.append(trace)
    layout = {
        "title": f"Price Chart for {ticker}",
        "xaxis": {"title": "Date"},
        "yaxis": {"title": "Price (USD)"},
        "showlegend": True,
        "legend": {"x": 0.02, "y": 0.98},
        "margin": {"l": 60, "r": 10, "t": 50, "b": 60},
        "hovermode": "x",
    }

    return {"data": data, "layout": layout}


def add_price_chart(figure, data, ticker):
    trace = go.Scatter(
        x=data.index, y=data["Close"], mode="lines", yaxis="y2", name=f"Price {ticker}"
    )

    figure["data"].append(trace)
    figure["layout"]["yaxis2"] = {
        "overlaying": "y",  # Nakładająca się na pierwszą oś y
        "side": "right",  # Po prawej stronie
        "title": "Price",  # Tytuł dla drugiej osi y
        "showgrid": False,  # Wyłączenie siatki dla drugiej osi y
    }
    return figure


if __name__ == "__main__":
    app.run(debug=True, port=2070)
