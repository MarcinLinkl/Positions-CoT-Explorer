<a name="readme-top"></a>

<div align="center">

  <h1 align="center">Positions Explorer: Unveiling Commitment of Traders Reports</h1>

  <p align="center">
    Unearth speculative trading positions across markets with data from the United States Commodity Futures Trading Commission (CFTC)
    <br />
    <a href="https://github.com/MarcinLinkl/Positions-Explorer"><strong>Explore the documentation »</strong></a>
    <br />
    <br />
    <!-- <a href="https://github.com/MarcinLinkl/Positions-Explorer">View Demo</a>
    · -->
    <a href="https://github.com/MarcinLinkl/Positions-Explorer/issues">Report Bug</a>
    ·
    <a href="https://github.com/MarcinLinkl/Positions-Explorer/issues">Request Feature</a>
  </p>
</div>

## Table of Contents
- [About the Project](#about-the-project)
  - [Application Overview](#application-overview)
  - [Charts: Visualizing Price Positions](#charts-visualizing-price-positions)
  - [Understanding CFTC and CoT Reports](#understanding-cftc-and-cot-reports)
  - [Trading Position Reports](#trading-position-reports)
  - [Use Cases](#use-cases)
- [Tech Stack](#tech-stack)

## About the Project

### Application Overview
Choose a report, commodity group, and commodity/exchange name. The "Select Price" dropdown will populate automatically.

The application showcases silver correlations (Pearson's) between prices and assets in futures contracts positioning for Commercial and Non-Commercial groups for Net (Long-Short) and Long positions of traders.

![App Interface](assets/1.jpg "Positions Explorer Interface")

### Charts: Visualizing Price 

The chart depicts the involvement of two major player groups: Commercial entities (silver producers) and Non-Commercial traders (speculators).

![App Interface](assets/2.jpg "Positions Explorer Charts")
Short description: _When the net futures position of the Commercial group declines (turns negative), it signifies a rise in hedging activities when the price drops. In such instances, these entities are safeguarding their interests. Therefore, considering buying becomes favorable when their positions are notably high.
Conversely, Non-Commercial positions tend to increase as prices surge. Low net positions for this group suggest that it could be a favorable time to buy, as they align with potential price uptrends._


### Understanding CFTC and CoT Reports

The **Commodity Futures Trading Commission** (CFTC) is an independent agency of the United States government responsible for regulating commodity futures, options, and swaps markets. The CFTC was established in 1974 through the Commodity Futures Trading Commission Act.
The **Commitments of Traders**, known as **CoT**, is a weekly market report where 20 or more traders hold positions equal to or above the reporting levels set by the **CFTC**. It is released every Friday at 3:30 p.m. ET and reflects traders' commitments on the prior Tuesday.

### Trading Position Reports

This section offers an overview of different trading position reports.

#### 1. Legacy Reports

Legacy reports provide a breakdown of trading positions by exchange, including both futures-only and combined futures and options positions. Reportable open interest positions in Legacy reports are classified into two categories:

1. Non-Commercial
2. Commercial Traders (Large Hedgers)

#### 2. Supplemental Reports

The Supplemental report covers 13 selected agricultural commodity contracts for combined futures and options positions, with a specific focus on the agricultural sector.

#### 3. Disaggregated Reports

Disaggregated reports offer insights into trading positions in various sectors: Agriculture, Petroleum and Products, Natural Gas and Products, Electricity, Metals, and other physical contracts.

Similar to Legacy reports, Disaggregated reports include both futures-only and combined futures and options positions. Reportable open interest positions in Disaggregated reports are classified into four categories:

1. Producer/Merchant/Processor/User
2. Swap Dealers
3. Managed Money
4. Other Reportables

#### 4. Traders in Financial Futures (TFF) Reports

TFF reports concentrate on financial contracts (Currencies, US Treasury Securities, Eurodollars, Stocks, VIX, Bloomberg Commodity Index)

### Use Cases

Trading position reports serve various purposes in financial and commodities markets:

1. **Risk Management:** Commercial traders ("hedgers") use reports to manage their exposure to price fluctuations. Analyzing commercial traders' positions provides insights into how they are positioning themselves to handle market risks.

2. **Speculative Insights:** Non-commercial traders ("large speculators") offer insights into speculative market sentiment. Their positions help traders and investors understand trends and make informed decisions.

3. **Price Forecasting:** Positions of both commercial and non-commercial traders can indicate potential price movements. Commercial traders' positions reflect potential supply and demand dynamics, while non-commercial traders' positions signal market trends.

4. **Market Analysis:** Reports are valuable for comprehensive market analysis. Studying positions by different trader types provides insights into market participants' behaviors and expectations.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Tech Stack

The application is powered by a combination of libraries, tools, and frameworks:

- ![Dash](https://img.shields.io/badge/-Dash-1E90FF?style=flat&logo=Dash&logoColor=white&labelColor=1E90FF): A Python framework for building interactive web applications for data visualization.
- ![Dash Bootstrap Components](https://img.shields.io/badge/-Dash%20Bootstrap%20Components-563D7C?style=flat&logo=Bootstrap&logoColor=white&labelColor=563D7C): Extends Dash with Bootstrap components for responsive designs.
- ![SQLite](https://img.shields.io/badge/-SQLite-003B57?style=flat&logo=SQLite&logoColor=white&labelColor=003B57): A lightweight, serverless database engine for data storage.
- ![Pandas](https://img.shields.io/badge/-Pandas-150458?style=flat&logo=Pandas&logoColor=white&labelColor=150458): A powerful data manipulation and analysis library for Python.
- ![yfinance](https://img.shields.io/badge/-yfinance-2B8FD9?style=flat&logo=Python&logoColor=white&labelColor=2B8FD9): Fetch financial data from Yahoo Finance.
- Custom Python scripts, like `utils.py` and `ticker_finder.py`, enhance functionality.
- ![SQLite Database](https://img.shields.io/badge/-SQLite-003B57?style=flat&logo=SQLite&logoColor=white&labelColor=003B57): Local database (`data.db`) for storing application data.
- ![Socrata API](https://img.shields.io/badge/-Socrata%20API-3498DB?style=flat&logo=Socrata&logoColor=white&labelColor=3498DB): Fetch relevant data.
- `reports_definitions.py`: Custom report definitions for structuring and managing data.
- `socrata_fetch_api`: [Socrata API](https://dev.socrata.com/) for data retrieval.
- `ticker_finder.py`: Script to find and manage tickers.
- `yahoo_tk_futures.json`: JSON file with Yahoo Finance futures ticker information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
