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

yahoo_tickers = load_yahoo_tk_data()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])
app.title = "Positions Explorer"
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
                            id="commodities-dropdown",
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
                        # className="custom-button",
                        # className="col-2 text-center",  # zmieniono na col-2
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
                        # className="custom-button",
                        # className="col-2 text-center",  # zmieniono na col-2
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
                        id="commodity-graph",
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


@app.callback(
    Output("correlation-card", "style"),
    Input("show-corr", "n_clicks"),
    Input("hide-corr", "n_clicks"),
)
def toggle_correlation_card(show_clicks, hide_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        return {"display": "none"}  # Domyślnie ukryj kartę

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "show-corr" and show_clicks:
        return {"display": "block"}  # Pokaż kartę po kliknięciu "Show Correlation Card"
    elif button_id == "hide-corr" and hide_clicks:
        return {"display": "none"}  # Ukryj kartę po kliknięciu "Hide Correlation Card"
    else:
        return dash.no_update  # Nie zmieniaj stanu karty


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
    if selected is None:
        return "Select a price chart:", None, 0, 0, [0, 0], {}

    ticker_dropdown = find_similar_ticker(selected, yahoo_tickers)
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
    return {"display": "none"} if chart_together_value != [True] else {}


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
    print("data frames: ", df_data)
    return df_data  # Zwróć listę ramek danych dla różnych typów


def map_column_name(report, column_name):
    category = root_cols_desc[report]
    name = ""
    print("column name: ", column_name)
    if column_name.startswith("pct_of_oi"):
        name += "Percentage of "
        column_name = column_name.replace("pct_of_oi_", "")
    else:
        name += "Positions of "
        column_name = column_name.replace("_positions", "")
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


@app.callback(
    Output("price-graph", "figure"),
    Output("commodity-graph", "figure"),
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
    df_price, df_positions, df_percentages = (
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
    )
    fig_price, fig_positions, fig_percentages = {}, {}, {}
    # this is univeral name, mnot t
    report = report_type.split("_")[1]
    card_percentage = []
    if market_commodity:
        print("market_commodity ", market_commodity)
        df_data = get_data(report_type, market_commodity, years)

        df_percentages = df_data.filter(regex=r"^pct_of_oi")
        df_positions = df_data.drop(columns=df_percentages.columns)
    if ticker:
        price_name = yahoo_tickers[ticker].upper()
        df_price = get_price_data(ticker, years)
        fig_price = create_figure(
            df_price, ticker, price_chart=True, price_name=price_name
        )
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
            correlation_text_positions = [
                html.P(
                    f"{map_column_name(report,col)} {'positive: +' if correlations_positions[col] >= 0 else 'negative: -'}{correlation:.2f}",
                    style={"margin": "5px"},
                )
                for col, correlation in sorted_correlations_positions.items()
            ]

            correlations_percentage = df_percentages.corr()["Close"].drop("Close")
            sorted_correlations_percentage = correlations_percentage.abs().sort_values(
                ascending=False
            )
            correlation_text_percentage = [
                html.P(
                    f"{map_column_name(report,col)} {'positive: +' if correlations_percentage[col] >= 0 else 'negative: -'}{correlation:.2f}",
                    style={"margin": "5px"},
                )
                for col, correlation in sorted_correlations_percentage.items()
            ]
            card_percentage = dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3(f"Correlations of {price_name.lower()}:"),
                            *correlation_text_positions,
                        ]
                    ),
                    dbc.Col(
                        [
                            html.H3(f"Correlations of {price_name.lower()}:"),
                            *correlation_text_percentage,
                        ]
                    ),
                ]
            )

    if market_commodity and positions and options:
        percentage_cols, positions_cols = [], []

        percentage_cols = [
            "pct_of_oi_" + x + "_" + y for x in positions for y in options
        ]
        print(percentage_cols)

        positions_cols = [x + "_positions_" + y for x in positions for y in options]
        print(positions_cols)
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

    # Generate the formatted correlation text
    return fig_price, fig_positions, card_percentage, fig_percentages


def get_price_data(ticker, year):
    start_date = f"{year[0]}-01-01" if year != [0, 0] else None
    end_date = f"{year[1]}-12-31" if year != [0, 0] else None
    print(start_date)
    print(end_date)
    return yf.download(ticker, start_date, end_date, "1wk")["Close"].to_frame()


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
            # "margin": {"l": 30, "r": 30, "t": 30, "b": 30},  # Marginesy wokół wykresu
            "title": {
                "text": name,
            },
            # Tytuł wykresu
            # "yaxis": {"title": y_desc, "y": "-0.5"},  # Etykieta osi Y
            "legend": {"orientation": "h", "y": 1.15},  # Legenda wykresu (poziomo)
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
                    "yaxis": "y2",  # Dodanie drugiej osi y dla ceny towaru
                    # "line": {"width": 1, "color": "firebrick", "dash": "line"},
                }
            )
            fig["layout"]["yaxis2"] = {
                "overlaying": "y",  # Nakładająca się na pierwszą oś y
                "side": "right",  # Po prawej stronie
                "title": "PRICE [$]",  # Tytuł dla drugiej osi y
                "showgrid": False,  # Wyłączenie siatki dla drugiej osi y
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


if __name__ == "__main__":
    app.run(debug=False, port=2020)
