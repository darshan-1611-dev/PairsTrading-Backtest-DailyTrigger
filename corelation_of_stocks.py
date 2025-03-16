import pandas as pd
import database as db
from datetime import datetime

#'''''''''''''''''''''''''''''''''''''''''''''''''
                                                 # 
STOCK_A_SYMBOL = "AXISBANK"                      # 
STOCK_B_SYMBOL = "ICICIBANK"                     # 
                                                 #
# for checking historical data                   #
START_DATE = datetime(2022, 1, 1) # YYYY-MM-DD   #
END_DATE = datetime.today()                      #
                                                 #
##################################################


db.connect_to_db()  # connect to the database 

# fetch stock A data
STOCK_A_data = pd.DataFrame(db.get_stock_details(STOCK_A_SYMBOL, start_date=START_DATE, end_date=END_DATE))

# fetch stock B data
STOCK_B_data = pd.DataFrame(db.get_stock_details(STOCK_B_SYMBOL, start_date=START_DATE, end_date=END_DATE))

stock_A_len = len(STOCK_A_data)
stock_B_len = len(STOCK_B_data)

# check if two stock data points is not same by length
if stock_A_len != stock_B_len:
    print( "\n", "Length of two stock is mismatched", "\n")
    print(f"{STOCK_A_SYMBOL} ({stock_A_len}): {STOCK_B_SYMBOL} ({stock_A_len})")
    exit()
    
# Corealtion of Closing price of the Stocks 
correlation_matrix_of_closing_price = pd.DataFrame({STOCK_A_SYMBOL: STOCK_A_data['CLOSE'], STOCK_B_SYMBOL: STOCK_B_data['CLOSE']}).corr()

print("\n", "Corealation of Closing Price: ", round(correlation_matrix_of_closing_price[STOCK_A_SYMBOL][STOCK_B_SYMBOL], 2))


################################################################


# Corealtion of daily return of the Stocks 
# daily return = [today’s closing price / previous day’s closing price] – 1
stock_A_daily_return = STOCK_A_data['CLOSE'] / STOCK_A_data['PREV. CLOSE'] - 1
stock_B_daily_return = STOCK_B_data['CLOSE'] / STOCK_B_data['PREV. CLOSE'] - 1

# calculate correlation of daily return
correlation_matrix_of_daily_return = pd.DataFrame({STOCK_A_SYMBOL: stock_A_daily_return, STOCK_B_SYMBOL: stock_B_daily_return}).corr()

print("\n", "Corealation of daily return: ", round(correlation_matrix_of_daily_return[STOCK_A_SYMBOL][STOCK_B_SYMBOL], 2))
