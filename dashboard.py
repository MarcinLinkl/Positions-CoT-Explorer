import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from utils import *
import sqlite3
import pandas as pd



yahoo_tk_data = load_yahoo_tk_data()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="report-dropdown",
                        options=get_reports_opts(),
                        placeholder="Select a report",
                        optionHeight=50,
                        className="dash-dropdown",
                        style={
                            "borderRadius": "15px",
                            "font-weight": "bold",
                        },
                    ),
                    className="col-lg-6 col-12 my-2",
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="commodities-dropdown",
                        placeholder="Select a commodity",
                        optionHeight=50,
                        className="dash-dropdown",
                        style={"borderRadius": "15px"},
                    ),
                    className="col-lg-6 col-12 my-2",
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="market-and-exchange-names-dropdown",
                        placeholder="Select a market/exchange",
                        optionHeight=50,
                        className="dash-dropdown",
                        style={"borderRadius": "15px"},
                    ),
                    className="col-12 my-2",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="ticker-dropdown",
                        options=get_chart_price_opts(yahoo_tk_data),
                        placeholder="Price chart",
                        value="SI=F",
                        optionHeight=50,
                        className="dash-bootstrap",
                        style={"borderRadius": "15px"},
                    ),
                    className="col-lg-5 col-12 my-2",
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="position-type",
                        options=[
                            {"label": "Commercial", "value": "comm_positions"},
                            {"label": "Non-Commercial", "value": "noncomm_positions"},
                            {"label": "Non-Reportable", "value": "nonrept_positions"},
                            {
                                "label": "Total Reportable",
                                "value": "tot_rept_positions",
                            },
                        ],
                        value="noncomm_positions",
                        multi=True,
                        placeholder="Select a position type",
                        className="dash-bootstrap",
                        style={"borderRadius": "15px", "text-align": "left"},
                    ),
                    className="col-lg-7 col-12 my-2",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.RadioItems(
                        id="chart-together",
                        options=[
                            {"label": "One graph", "value": True},
                            {"label": "Two graphs", "value": False},
                        ],
                        value=True,
                        labelStyle={
                            "display": "inline-block",
                            "margin": "0 25px",
                            "text-align": "center",
                            "font-size": "18px",
                        },
                        className="text-center",
                    ),
                    className="col-md-5 col-12 my-2",
                ),
                dbc.Col(
                    dcc.Checklist(
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
        dbc.Row(
            [
                dbc.Col(
                    dcc.RangeSlider(
                        id="year-slider",
                        step=1,
                        className="col-12 px-10 custom-range-slider",
                    ),
                    className="px-2",
                ),
            ],
            className="p-2",
        ),
    ],
    fluid=True,
)

@app.callback(
    Output("commodities-dropdown", "options"),
    Input("report-dropdown", "value")
)
def update_commodities_dropdown(report):
    if report is None:
        return []
    return get_commodities_opts(report)

@app.callback(
    Output("market-and-exchange-names-dropdown", "options"),
    Input("commodities-dropdown", "value"),
    Input("report-dropdown", "value")
)
def update_market_dropdown(selected_commodity, selected_report):
    if selected_commodity is None:
        return []
    return get_market_opts(selected_commodity, selected_report)

@app.callback(
    Output("year-slider", "min"),
    Output("year-slider", "max"),
    Output("year-slider", "value"),
    Output("year-slider", "marks"),
    Input("market-and-exchange-names-dropdown", "value")
)
def update_year_slider(selected):
    if selected is None:
        return 0, 0, [0, 0], {}
    year_slider_opts=get_slider_opts(selected)
    print(year_slider_opts)
    return year_slider_opts

if __name__ == "__main__":
    app.run(debug=True, port=2070)
