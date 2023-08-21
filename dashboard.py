import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from utils import *
from ticker_finder import *
import sqlite3
import pandas as pd
import plotly.express as px


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
                        value=[False],
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
        "Price chart not found; you may need to select one manually:"
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


@app.callback(
    Output("price-graph", "figure"),
    Output("commodity-graph", "figure"),
    Input("market-and-exchange-names-dropdown", "value"),
    Input("position-type", "value"),
    Input("year-slider", "value"),
    Input("show-option", "value"),
    Input("chart-price-dropdown", "value"),
    Input("add-price-line", "value"),
)
def update_graphs_callback(selected, positions, year, options, ticker, add_price):
    if ticker:
        print("Download: ", ticker)
        if year != [0, 0]:
            df_price = yf.download(
                ticker,
                start=f"{year[0]}-01-01",
                end=f"{year[1]}-12-31",
                interval="1wk",
            )["Close"].to_frame()
        else:
            df_price = yf.download(
                ticker,
                interval="1wk",
            )["Close"].to_frame()

        fig = px.line(
            df_price,
            x=df_price.index,
            y="Close",
            title=f"Price Chart for {ticker}",
        )

        fig.update_traces(line=dict(color="blue", width=2))  # Dostosowanie linii
        fig.update_xaxes(title_text="Date", tickformat="%b %Y")  # Format daty
        fig.update_yaxes(title_text="Price (USD)")  # Etykieta osi y
        fig.update_layout(
            plot_bgcolor="white",  # Tło wykresu
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
        )

        fig.update_xaxes(rangeslider_visible=True)
        return fig, {}
    return {}, {}


def load_date(selected, position, year, options, chart_ticker, add_price):
    start_year, end_year = year

    conn = sqlite3.connect("data.db")
    return {}


if __name__ == "__main__":
    app.run(debug=True, port=2070)
