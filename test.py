'''
import yfinance as yf
#dat = yf.Ticker("MSFT")

spy = yf.Ticker('SPY').funds_data
print(spy.description)
print(spy.top_holdings)'''

from datetime import date, timedelta
from jugaad_data.nse import stock_df


start_date = date(2023,8,12)
end_date = date(2025,3,5)
stock_symbol="HDFC"

df = stock_df(symbol=stock_symbol, from_date=start_date,
                to_date=end_date, series="EQ")
      
expected_columns = [
    'CH_TIMESTAMP', 'CH_SERIES', 'CH_OPENING_PRICE', 'CH_TRADE_HIGH_PRICE',
    'CH_TRADE_LOW_PRICE', 'CH_PREVIOUS_CLS_PRICE', 'CH_LAST_TRADED_PRICE',
    'CH_CLOSING_PRICE', 'VWAP', 'CH_52WEEK_HIGH_PRICE', 'CH_52WEEK_LOW_PRICE',
    'CH_TOT_TRADED_QTY', 'CH_TOT_TRADED_VAL', 'CH_TOTAL_TRADES', 'CH_SYMBOL'
]

# Check if the columns exist in the DataFrame
existing_columns = [col for col in expected_columns if col in df.columns]
print(f"Found columns: {existing_columns}")

# Use only the existing columns
df = df[existing_columns]
