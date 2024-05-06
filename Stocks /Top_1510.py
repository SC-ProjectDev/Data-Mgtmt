import yfinance as yf
from openpyxl import Workbook
from datetime import datetime, timedelta
import pandas as pd

# Adjusted function to fetch stock data
def fetch_stock_data(stock_symbol, start_date, end_date):
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date, interval='15m')
    return stock_data

# Calculate the start and end dates for the past week
end_date = datetime(2024, 5, 6)
start_date = end_date - timedelta(days=15)

# Format dates for yfinance
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

# List of stock symbols
symbols = ['SPY', 'MSFT', 'AAPL', 'NVDA', 'AMZN', 'META', 'GOOGL', 'GOOG', 'SMCI', 'AVGO', 'LLY', 'BRK-B', 'ADBE', 'CSCO', 'ACN', 'ORCL', 'CRM' ]

# Fetch stock data for the past week, in 30-minute increments
stock_data = {symbol: fetch_stock_data(symbol, start_date_str, end_date_str) for symbol in symbols}

# Create a new workbook and worksheet
wb = Workbook()
ws = wb.active

# Write headers with added '_Volume'
header_row = ['Date_Time']
for symbol in symbols:
    header_row.extend([f"{symbol}_Open", f"{symbol}_High", f"{symbol}_Low", f"{symbol}_Close", f"{symbol}_Volume"])
ws.append(header_row)

# Find the union of all timestamps across fetched data
all_timestamps = sorted(set.union(*[set(stock_data[symbol].index) for symbol in symbols]))

# Write data for each timestamp
for timestamp in all_timestamps:
    data_row = [timestamp]
    for symbol in symbols:
        if timestamp in stock_data[symbol].index:
            row = stock_data[symbol].loc[timestamp]
            data_row.extend([row['Open'], row['High'], row['Low'], row['Close'], row['Volume']])
        else:
            # If a stock doesn't have data for this timestamp, fill with None
            data_row.extend([None, None, None, None, None])
    ws.append(data_row)

# Save the workbook
wb.save("05052024.xlsx")

