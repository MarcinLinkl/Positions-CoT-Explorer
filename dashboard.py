import os
import json
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output

# Local imports
from data_operations import *
from reports_cols import root_cols_desc
from ticker_finder import find_similar_ticker
from utils import *
from fetch_data import fetch_all_reports
from quick_fix_for_nulls import cleanup_commodity_subgroup_nulls

# Load ticker data from json file for loading yfinance data

with open("yahoo_tk_futures.json") as f:
    tickers_dict = json.load(f)

price_tickers_labels_dropdown = [{"label": f"{j.upper()}", "value": i } for i, j in tickers_dict.items()]


# Here we load the tickers and making labels for dropdown menu - with dumped dict to string as a values ( with json.dumps)
# It's important to use json.dumps() to convert the dictionary to a JSON string before passing it to the dropdown options.
# This ensures that the data is in a format that Dash can handle without issues, - it can't handle dicts directly.
# Dash uses JSON to serialize data for transmission between the server and client.
# Later, when you need to use the data, you can convert it back from JSON string to a dictionary using json.loads()


# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])
app.title = "Positions Explorer"

# Database check and initialization
if os.path.exists("data.db"):
    print("Checking for new reports...")
    check_for_new_records()
    cleanup_commodity_subgroup_nulls()
else:
    print("Database does not exist. Creating database.")
    fetch_all_reports()
    cleanup_commodity_subgroup_nulls()

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
                            options=get_reports_opts(),  # Populate with options from get_reports_opts
                            value="report_legacy_futures_only",  # Default value
                            placeholder="Select a report",
                            optionHeight=50,
                            className="dash-dropdown",
                            style={"borderRadius": "15px"},
                            
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
                        dbc.Label("Select a specific commodity market/commodity exchange name: "),
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
                            id="years-slider",
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
                            options=price_tickers_labels_dropdown,
                            placeholder="Select price",
                            optionHeight=50,
                            value="^SP500-30",
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
                            id="positions-types",
                            multi=True,
                            placeholder="Select a positions types",
                            className="dash-bootstrap",
                            style={"borderRadius": "15px"},
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
                        options=[{"label": "Display additional price", "value": True}],
                        value=[True],
                        inline=True,
                        switch=True,
                        className="text-center",
                    ),
                    className="col-lg-3 col-6 my-2",
                ),
                dbc.Col(
                    dbc.Checklist(
                        id="add-price-line",
                        options=[{"label": "Add price line", "value": True}],
                        value=False,
                        inline=True,
                        switch=True,
                        className="text-center",
                        
                    ),
                    className="col-lg-2 col-6 my-2",
                ),
                dbc.Col(
                    dbc.Button(
                        "Show correlations",
                        id="show-corr",
                        color="success",
                       
                    ),
                    className="col-lg-2 col-3 my-2 text-center",
                ),
                dbc.Col(
                    dbc.Button(
                        "Hide correlations",
                        id="hide-corr",
                        color="success",
                    ),
                    className="col-lg-2 col-3 my-2 text-center",
                ),
                dbc.Col(
                    dbc.Checklist(
                        id="show-options",
                        options=[{"label": i.capitalize(), "value": i} for i in ["net", "long", "short"]],
                        value=["net"],
                        inline=True,
                        className="text-center",
                    ),
                    className="col-lg-3 col-6 my-2",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Card([html.Div(id="correlation-card", style={"display": "none"})]),
                    className="col-12 my-2 mx-auto text-center"),
                dbc.Col(dcc.Graph(id="price-graph"), className="col-12 my-2"),
                dbc.Col(dcc.Graph(id="positions-graph"), className="col-12 my-2"),
                dbc.Col(dcc.Graph(id="percentage-graph"), className="col-12 my-2"),
            ],
            className="p-2",
        ),
    ],
    fluid=True
)

# Callbacks to update components dynamically
@app.callback(
    Output("commodities-subgroup-dropdown", "options"),
    Input("report-dropdown", "value"),
)
def update_commodities_dropdown(report):
    if report is None:
        return []
    return get_commodities_subgroup_opts(report)

@app.callback(
    Output("market-and-exchange-names-dropdown", "options"),
    Input("commodities-subgroup-dropdown", "value"),
    Input("report-dropdown", "value"),
)
def update_market_dropdown(selected_commodity_subgroup, selected_report):
    if selected_report and not selected_commodity_subgroup:
        return get_market_opts(report=selected_report)
    elif selected_report and selected_commodity_subgroup:
        return get_market_opts(selected_report, selected_commodity_subgroup)
    else:
        return [], []

@app.callback(
    Output("price-chart-label", "children"),
    Output("chart-price-dropdown", "value"),
    Output("years-slider", "min"),
    Output("years-slider", "max"),
    Output("years-slider", "value"),
    Output("years-slider", "marks"),
    Input("market-and-exchange-names-dropdown", "value"),
    Input("report-dropdown", "value"),
)
def update_year_slider_and_price_dropdown_value(selected, report):
    if selected is None or report is None:
        return "Select a price chart:", None, 0, 0, [0, 0], {}
    
    selected = json.loads(selected)
    name_market = selected["name_market"]
  
    ticker_dropdown = find_similar_ticker(name_market, tickers_dict)
    # print in red 
    # print(f"\033[31mticker_dropdown: {ticker_dropdown}\033[0m")

    price_chart_label = (
        "Price chart not found; may need to select one manually:" if ticker_dropdown is None
        else f"Price chart found: {ticker_dropdown}, you can adjust manually if needed"
    )
    

    min_y, max_y, values, marks = get_slider_opts(selected["cftc_code"], report)
    return price_chart_label, ticker_dropdown, min_y, max_y, values, marks

@app.callback(
    Output("positions-types", "options"),
    Output("positions-types", "value"),
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
    Input("positions-types", "value"),
    Input("years-slider", "value"),
    Input("show-options", "value"),
    Input("chart-price-dropdown", "value"),
    Input("add-price-line", "value"),
)
def update_graphs_callback(
    report_type, market_commodity_str, positions, years, options, ticker, include_price):

    if market_commodity_str is not None:
        print(f"market_commodity_str: {market_commodity_str}")
        market_commodity = json.loads(market_commodity_str)

    # print("market_commodity: ", market_commodity)
    ticker_name = tickers_dict.get(ticker, None)

    if market_commodity_str is None:
        if ticker:
            print(" We are going to show the price graph only")
            return make_only_price_graph(ticker,ticker_name), dash.no_update, dash.no_update, dash.no_update
        
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    return make_graphs_and_cards(report_type, market_commodity, positions, years, options, ticker,ticker_name, include_price)




# Run the app
if __name__ == "__main__":
    app.run(debug=False, port=2077)