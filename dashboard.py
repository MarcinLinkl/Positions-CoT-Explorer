import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from data_operations import *
from reports_cols import root_cols_desc
from ticker_finder import find_similar_ticker
from utils import *
from fetch_data import fetch_all_reports

# Load ticker data from Yahoo Finance
yahoo_tickers = load_yahoo_tk_data()

# Create a Dash web application instance
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])

if os.path.exists("data.db"):
    print("Checking for new reports...")
    check_for_new_records()
else:
    print("Database does not exist.")
    print("Creating database.")
    fetch_all_reports()


app.title = "Positions Explorer"

# Define the layout of the web application
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
                        dbc.Label("Select a commodity subgroup:"),
                        dcc.Dropdown(
                            id="commodities-subgroup-dropdown",
                            placeholder="Select a commodity group",
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
                                {"label": f"Price of {j.lower()}", "value": i}
                                for i, j in yahoo_tickers.items()
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
                    className="col-lg-2 col-3 my-2",
                ),
                dbc.Col(
                    dbc.Button(
                        "Show correlations",
                        id="show-corr",
                        color="success",
                        style={
                            "display": "inline-block",
                            "max-height": "30px",
                            "border-radius": "15px",
                            "text-align": "center",
                            "margin": "0",
                            "padding": "0",
                            "width": "calc(90%)",
                        },
                    ),
                    className="col-lg-2 col-3 my-2 text-center",
                ),
                dbc.Col(
                    dbc.Button(
                        "Hide correlations",
                        id="hide-corr",
                        color="success",
                        style={
                            "display": "inline-block",
                            "max-height": "30px",
                            "border-radius": "15px",
                            "text-align": "center",
                            "margin": "0",
                            "padding": "0",
                            "width": "calc(90%)",
                        },
                    ),
                    className="col-lg-2 col-3 my-2 text-center",
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
                    className="col-lg-3 col-3 my-2",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [html.Div(id="correlation-card", style={"display": "none"})],
                    ),
                    className="col-12 my-2 mx-auto text-center",
                ),
                dbc.Col(
                    dcc.Graph(
                        id="price-graph",
                        className="col-12 my-2",
                    ),
                    className="col-12",
                ),
                dbc.Col(
                    dcc.Graph(
                        id="positions-graph",
                        className="col-12 my-2",
                    ),
                    className="col-12",
                ),
                dbc.Col(
                    dcc.Graph(
                        id="percentage-graph",
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


# Callback to update commodities dropdown options based on the selected report
@app.callback(
    Output("commodities-subgroup-dropdown", "options"),
    Input("report-dropdown", "value"),
)
def update_commodities_dropdown(report):
    if report is None:
        return []
    return get_commodities_subgroup_opts(report)


# Callback to update market dropdown options based on selected commodity and report
@app.callback(
    Output("market-and-exchange-names-dropdown", "options"),
    Input("commodities-subgroup-dropdown", "value"),
    Input("report-dropdown", "value"),
)
def update_market_dropdown(selected_commodity, selected_report):
    if selected_commodity is None or selected_report is None:
        return [], []
    return get_market_opts(selected_commodity, selected_report)


# Callback to update various components including price chart label, slider, and more
@app.callback(
    Output("price-chart-label", "children"),
    Output("chart-price-dropdown", "value"),
    Output("year-slider", "min"),
    Output("year-slider", "max"),
    Output("year-slider", "value"),
    Output("year-slider", "marks"),
    Input("market-and-exchange-names-dropdown", "value"),
    Input("report-dropdown", "value"),
)
def update_year_slider_and_price_dropdown_value(selected, report):
    if selected is None:
        return "Select a price chart:", None, 0, 0, [0, 0], {}

    name_market = json.loads(selected)["name_market"]
    ticker_dropdown = find_similar_ticker(name_market, yahoo_tickers)
    price_chart_label = (
        "Price chart not found; may need to select one manually:"
        if ticker_dropdown is None
        else f"Price chart found: {ticker_dropdown}, you can adjust manually if needed"
    )

    min_y, max_y, values, marks = get_slider_opts(selected, report)
    return price_chart_label, ticker_dropdown, min_y, max_y, values, marks


# Callback to update position types based on the selected report
@app.callback(
    Output("position-type", "options"),
    Output("position-type", "value"),
    Input("report-dropdown", "value"),
)
def update_position_types(report):
    if report is None:
        return [], []
    selected_report = report.split("_")[1]
    categories = root_cols_desc.get(selected_report, {})
    options = [{"label": label, "value": value} for value, label in categories.items()]
    default_value = options[1]["value"] if options else None

    return options, [default_value]


# Callback to toggle the visibility of the price graph based on user input
@app.callback(
    Output("price-graph", "style"),
    Input("display-chart", "value"),
)
def toggle_price_graph_visibility(chart_together_value):
    return {"display": "none"} if chart_together_value != [True] else {}


# Callback to toggle the correlation card's visibility
@app.callback(
    Output("correlation-card", "style"),
    Input("show-corr", "n_clicks"),
    Input("hide-corr", "n_clicks"),
)
def toggle_correlation_card(show_clicks, hide_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return {"display": "none"}

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "show-corr" and show_clicks:
        return {"display": "block"}
    elif button_id == "hide-corr" and hide_clicks:
        return {"display": "none"}
    else:
        return dash.no_update


# Callback to update various graphs based on user input
@app.callback(
    Output("price-graph", "figure"),
    Output("positions-graph", "figure"),
    Output("correlation-card", "children"),
    Output("percentage-graph", "figure"),
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
    return make_graphs_card(
        yahoo_tickers,
        report_type,
        market_commodity,
        positions,
        years,
        options,
        ticker,
        add_price,
    )


# Main entry point of the application
if __name__ == "__main__":
    app.run(debug=False, port=2077)
