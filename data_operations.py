# Import necessary libraries
from dash import html
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import yfinance as yf
from reports_cols import root_cols_desc, root_cols

# in root_cols_desc we have the normal description of the each raw columns for each report type that we get from scopa source 
# like "tot_rept": "Total Reportable",
# we need to map the columns for better readability in pearson correlation cards
def map_column_name(report, column_name):
   
    category = root_cols_desc.get(report, {})
    

    column_name = column_name.replace("pct_of_oi_", "").replace("_positions", "")
    suffix_map = {"_net": " Net", "_short": " Short", "_long": " Long"}
    
    for key, suffix in suffix_map.items():
        if column_name.endswith(key):
            column_name = column_name.replace(key, "")
            return category.get(column_name, column_name) + suffix
    
    return category.get(column_name, column_name)

# Function to retrieve data from the database based on report type and CFTC code
def get_data(report_type, cftc_code, years):
    roots = root_cols[report_type.split("_")[1]]
    cols = [f"{item}_{suffix}" for item in roots for suffix in ["net", "long", "short"]]
    cols.append("open_interest")
    conn = sqlite3.connect("data.db")
    query = f"""
    SELECT report_date_as_yyyy_mm_dd, {', '.join(cols)}
    FROM {report_type}
    WHERE cftc_contract_market_code = ?
    AND report_date_as_yyyy_mm_dd BETWEEN ? AND ?
    ORDER BY 1 ASC"""
    params = (cftc_code, f"{years[0]}-01-01", f"{years[1]}-12-31")
    df = pd.read_sql(query, conn, params=params).rename(columns={"report_date_as_yyyy_mm_dd": "Date"})
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    conn.close()
    return df

# Function to retrieve price data from Yahoo Finance
def get_price_data(ticker, years=None):
    try:
        if years is None:
            return yf.download(ticker, interval="1wk")["Close"]
        else:
            start_date, end_date = f"{years[0]}-01-01", f"{years[1]}-12-31"
            return yf.download(ticker, start=start_date, end=end_date, interval="1wk")["Close"]
    except Exception as e:
        print(f"Error fetching price data: {e}")
        return pd.Series()


def prepare_chart_data(report_type, cftc_code, years, ticker):
    df_positions, df_percentages, df_price = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    if cftc_code:
        df_data = get_data(report_type, cftc_code, years)
        df_percentages = df_data.filter(like="pct_of_oi")
        df_positions = df_data.drop(columns=df_percentages.columns)
    if ticker:
        df_price = get_price_data(ticker, years)
        print(f"Price data for {ticker} from {years[0]} to {years[1]}: {df_price}")
    return {"price": df_price, "positions": df_positions, "percentages": df_percentages}



def create_figure(df, title, selected_columns=None, price_chart=True):

    # decsription = if 
     # Initialize the chart layout
    fig = {
        "data": [],
        "layout": {
            "title": {
                "text": title,
            },
            "legend": {"orientation": "h", "y": 1.15},
        },
    }
    
    if price_chart and not df.empty:
        # If price chart is selected, add the price data to the chart
        # Add price data with y-axis on the right to the chart 
        fig["data"].append({"x": df.index, "y": df.iloc[:, 0], "type": "line", "name": f"PRICE of {title} [$]", "yaxis": "y2"}) # assuming the first column is the price data
        fig["layout"]["yaxis2"] = {"overlaying": "y", "side": "right", "title": "PRICE [$]", "showgrid": False}

    if selected_columns:
        for col in selected_columns:
            #  here we are using the column name from the list of selected columns
            # Add position data with y-axis on the left to the chart
            # If percentage chart is selected, name will be adjusted accordingly in that case.
            fig["data"].append({"x": df.index, "y": df[col], "type": "line", "name": col.replace("pct_of_oi_", "Percentage of ").replace("_", " ").title(), "line": {"width": 1}, "yaxis": "y1"})
    
    return fig




def make_only_price_graph(ticker, ticker_name):
    df_price = get_price_data(ticker)
    print("Price data:", df_price)
    return create_fig_price(df_price, ticker_name) if not df_price.empty else {}

def create_fig_price(data_dict, title, open_interest=False):

    df = data_dict.get("price", pd.DataFrame())
    df_open_interest = data_dict.get("positions", pd.DataFrame())
    df_open_interest=df_open_interest[["open_interest"]] if "open_interest" in df_open_interest.columns else pd.DataFrame()
    if isinstance(df, pd.Series):
        df = df.to_frame(name="price")

    fig = {
        "data": [], 
        "layout": {
            "title":{"text": f"{title} Price [$]"}, 
            "legend": {"orientation": "h", "y": 1.15}
            },
        }
    if not df.empty:
        fig["data"].append({
            "x": df.index, "y": df.iloc[:, 0] # assuming the first column is the price data
            , "type": "line", 
            "name": f"PRICE of {title} [$]", "yaxis": "y2"
        })
        fig["layout"]["yaxis2"] = {"overlaying": "y", "side": "right", "title": "PRICE [$]", "showgrid": False}

        
    
    print("DataFrame columns:", df.columns)
    if not df_open_interest.empty and open_interest:
        fig["data"].append({
            "x": df_open_interest.index, "y": df_open_interest.iloc[:, 0], "type": "line", 
            "name": "Open Interest", "line": {"color": "gray", "dash": "dot"}
        })
        # fig["layout"]["yaxis3"] = {"overlaying": "y", "side": "left", "title": "Open Interest", "showgrid": False}


    print("**" * 20)
    
    return fig


def create_figure_positions(df, title, selected_cols=None, include_price=False, ticker_name=None, open_interest=False):
    fig = {
        "data": [],
        "layout": {
            "title": {"text": f"{title}"},
            "legend": {"orientation": "h", "y": 1.15},
            },
        }
    if include_price and not df["price"].empty:
        fig["data"].append({
            "x": df["price"].index, "y": df["price"].iloc[:, 0], "type": "line", 
            "name": f"PRICE of {ticker_name} [$]", "yaxis": "y2"
        })
        fig["layout"]["yaxis2"] = {"overlaying": "y", "side": "right", "title": "PRICE [$]", "showgrid": False}
    if open_interest and "open_interest" in df["positions"].columns:
        fig["data"].append({
            "x": df["positions"].index, "y": df["positions"]["open_interest"], 
            "type": "line", "name": "Open Interest", "line": {"color": "gray", "dash": "dot"}
        })
    print("**" * 20)
    print("Selected columns for positions chart:", df)    
    if selected_cols:
        # Add position data to the chart on the left y-axis
        for col in selected_cols:
            fig["data"].append({"x": df["positions"].index, "y": df["positions"][col], 
                "type": "line", "name": col.replace("_", " ").title()})
    return fig
                 
def create_figure_percentages(df, title, selected_cols=None, include_price=False, ticker_name=None):
    fig = {
        "data": [],
        "layout": {
            "title": {"text": f"{title}"},
            "legend": {"orientation": "h", "y": 1.15},
        },
    }
    
    if include_price and not df["price"].empty:
        fig["data"].append({
            "x": df["price"].index, 
            "y": df["price"].iloc[:, 0], 
            "type": "line",  
            "name": f"PRICE of {ticker_name} [$]", 
            "yaxis": "y2",
            "line": {"color": "black"} 
        })
        fig["layout"]["yaxis2"] = {
            "overlaying": "y", 
            "side": "right", 
            "title": "PRICE [$]", 
            "showgrid": False
        }
    
    if selected_cols:
        for col in selected_cols:
            fig["data"].append({
                "x": df["percentages"].index, 
                "y": df["percentages"][col], 
                "type": "line",  
                "name": col.replace("pct_of_oi_", "Percentage of ").replace("_", " ").title()
            })
    
    return fig


def make_graphs_and_cards(report_type, market_commodity, selected_positions,years, options, ticker, ticker_name, include_price , open_interest):

    chart_data = prepare_chart_data(report_type, market_commodity['cftc_code'], years, ticker)
    # in red  ** is for debugging purposes to check the data that we are getting from the database and yahoo finance before creating the charts, we can remove it later
    # print in red
    print("\033[91m" + "**" * 200 + "\033[0m")
  
    fig_price = create_fig_price(chart_data , ticker_name ,open_interest) if ticker or open_interest else {}
    if market_commodity:
        positions_title = "Positions Of " + market_commodity["name_market"] + " [" + market_commodity["units"] + "]"
        percentages_title = "Percentage Positions Of " + market_commodity["name_market"] + " [%]"
        position_cols = [f"{pos}_positions_{opt}" for pos in selected_positions for opt in options]
        percentage_cols = ["pct_of_oi_" + x + "_" + y for x in selected_positions for y in options]
        fig_positions = create_figure_positions(chart_data, positions_title, position_cols, include_price, ticker_name, open_interest) 
        fig_percentages = create_figure_percentages(chart_data, percentages_title, percentage_cols, include_price, ticker_name) if selected_positions and options else {}
   
    if market_commodity and ticker:
         # df_price_weekly = chart_data["price"].resample("W").mean()
        
        df_positions = pd.concat([chart_data["price"], chart_data["positions"]], axis=1).ffill().dropna()
        df_percentages = pd.concat([chart_data["price"], chart_data["percentages"]], axis=1).ffill().dropna()
     

        # Calculate correlations for positions and percentages
        corr_positions = df_positions.corr().iloc[1:, 0]
        corr_percentages = df_percentages.corr().iloc[1:, 0]


        # Get the correlation text for positions and percentages

        # Extract the report name core type from the provided string // legacy istead of  report_legacy_futures_only
        # For making whole tekst description more readable like -> Commercial Long negative (for eg. if legacy report and commercial cols)
        report_core_name = report_type.split("_")[1]

        correlation_text_positions = get_correlation_text(report_core_name, corr_positions)
        correlation_text_percentages = get_correlation_text(report_core_name, corr_percentages)
     
        card_correlations = get_correlation_card(
            ticker_name,
            correlation_text_positions,
            correlation_text_percentages,
        )
        
    else:
        
        card_correlations = []

   
    return fig_price, fig_positions, card_correlations, fig_percentages



# Function to get correlation text for the report
def get_correlation_text(report, correlations):
    # Sort correlations by absolute value
    sorted_correlations = sorted(
        correlations.items(), key=lambda x: abs(x[1]), reverse=True
    )
    # Create a list of correlation text
    return [
        html.P(
            f"{map_column_name(report, col)} {'positive: +' if correlation >= 0 else 'negative: '}{correlation:.2f}",
            style={"margin": "5px"},
        )
        for col, correlation in sorted_correlations
    ]

# Function to create a correlation card
def get_correlation_card(
    price_name, correlation_text_positions, correlation_text_percentage
):
    # Create a card with correlation information
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H4(f"PEARSON'S CORRELATIONS OF {price_name.upper()}:"),
                    *correlation_text_positions,
                ]
            ),
            dbc.Col(
                [
                    html.H4(f"PEARSON'S CORRELATIONS OF {price_name.upper()} [%]:"),
                    *correlation_text_percentage,
                ]
            ),
        ]
    )
