import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from utils import *
from ticker_finder import *
import sqlite3
import pandas as pd


yahoo_tk_data = load_yahoo_tk_data()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Select report:"),
                        dcc.Dropdown(
                            id="report-dropdown",
                            options=get_reports_opts(),
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
                            min=0,
                            max=1,
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
                            id="ticker-dropdown",
                            options=get_chart_price_opts(yahoo_tk_data),
                            placeholder="Select price",
                            optionHeight=50,
                            className="dash-bootstrap",
                            style={"borderRadius": "15px"},
                        ),
                    ],
                    className="col-lg-5 col-12 my-2 text-center",
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
                            value="noncomm_positions",
                            multi=True,
                            placeholder="Select a position type",
                            className="dash-bootstrap",
                            style={
                                "borderRadius": "15px",
                                # "text-align": "left"
                            },
                        ),
                    ],
                    className="col-lg-7 col-12 my-2 text-center",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        # [  dbc.Label("Display additional graph of price:"),
                        dbc.Checklist(
                            id="chart-together",
                            options=[
                                {
                                    "label": "Display additional price chart",
                                    "value": True,
                                },
                            ],
                            value=[True],
                            inline=True,
                            labelStyle={
                                "display": "inline-block",
                                "margin": "0 25px",
                                "text-align": "center",
                                "font-size": "18px",
                            },
                            switch=True,
                            className="text-center",
                        ),
                    ],
                    className="col-md-5 col-12 my-2 text-center",
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
                            "margin": "0 25px",
                            "font-weight": "bold",
                            "font-size": "18px",
                        },
                        className="text-center",
                    ),
                    className="col-md-7 col-12 my-2",
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
    Output("ticker-dropdown", "value"),
    Output("year-slider", "min"),
    Output("year-slider", "max"),
    Output("year-slider", "value"),
    Output("year-slider", "marks"),
    Input("market-and-exchange-names-dropdown", "value"),
)
def update_year_slider_and_price_dropdown_value(selected):
    if selected is None:
        return "Select a price chart:", None, 0, 0, [0, 0], {}

    ticker_dropdown = find_similar_ticker(selected, yahoo_tk_data)
    price_chart_label = (
        "Price chart not found; you may need to select one manually:"
        if ticker_dropdown is None
        else f"Price chart found: {ticker_dropdown}, you can adjust manually if needed"
    )

    min_year, max_year, slider_value, slider_marks = get_slider_opts(selected)
    # Dodaj opis w zależności od znalezionego tickera

    return (
        price_chart_label,
        ticker_dropdown,
        min_year,
        max_year,
        slider_value,
        slider_marks,
    )


@app.callback(
    Output("price-graph", "style"),
    Input("chart-together", "value"),
)
def toggle_price_graph_visibility(chart_together_value):
    if chart_together_value == [True]:
        return {}
    else:
        return {"display": "none"}


if __name__ == "__main__":
    app.run(debug=True, port=2070)
