import main as st
from datetime import datetime, timedelta
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


START_DATE = datetime(2022, 1, 1)                  
END_DATE = datetime(2022, 12, 31)

STOP_DATE = datetime(2025, 3, 13)
#STOP_DATE = datetime(2024, 12, 15)
stop_itr = int((STOP_DATE - END_DATE).days)


LONG_TRIGGER_MIN = 0.025
LONG_TRIGGER_MAX = 0.03 
LONG_TRIGGER_TARGET =  0.25  # or lower
LONG_TRIGGER_TARGET_MIN =  0.23  
LONG_TRIGGER_TARGET_MAX =  0.27  
LONG_TRIGGER_STOPLOSS = 0.003 # or higher
LONG_TRIGGER_STOPLOSS_MIN = 0.001 
LONG_TRIGGER_STOPLOSS_MAX = 0.003 


SHORT_TRIGGER_MIN = 0.975
SHORT_TRIGGER_MAX = 0.997 
SHORT_TRIGGER_TARGET =  0.975  # or lower
SHORT_TRIGGER_TARGET_MIN =  0.975  
SHORT_TRIGGER_TARGET_MAX =  0.27  
SHORT_TRIGGER_STOPLOSS = 0.997 # or higher
SHORT_TRIGGER_STOPLOSS_MIN = 0.001 
SHORT_TRIGGER_STOPLOSS_MAX = 0.003

STOCK_A_LOT_SIZE = 625
STOCK_B_LOT_SIZE = 700

TRADE_LONG_BUY_STOCK = "AXISBANK" 
TRADE_LONG_SELL_STOCK = "ICICIBANK" 

TRADE_A_STOCK = "AXISBANK" 
TRADE_B_STOCK = "ICICIBANK" 

TARGET_FLAG= "TARGET_HIT"
STOPLOSS_FLAG= "STOPLOSS_HIT"

LONG_TRADE_FLAG = "LONG"
SHORT_TRADE_FLAG = "SHORT"

trades_data = []  # for long data entry 

def trade_long_entry(stock_df, buy_stock, sell_stock, trade_flag):
    trade_details = {
    "trade_close":  False,
    "trade": trade_flag,
    "buy": {"stock_name": buy_stock, 
     "date": stock_df["DATE"].iloc[0],
     "buy_price": stock_df[buy_stock].iloc[0],
     "quatity": STOCK_A_LOT_SIZE,
     "amount": stock_df[buy_stock].iloc[0] * STOCK_A_LOT_SIZE,
     "ratio": stock_df["ratio"].iloc[0],
     "norm_dist_of_ratio": stock_df["norm_dist_of_ratio"].iloc[0]
    },
    "sell": {"stock_name": sell_stock, 
     "date": stock_df["DATE"].iloc[0],
     "sell_price": stock_df[sell_stock].iloc[0],
     "quatity": STOCK_B_LOT_SIZE,
     "amount": stock_df[sell_stock].iloc[0] * STOCK_B_LOT_SIZE,
     "ratio": stock_df["ratio"].iloc[0],
     "norm_dist_of_ratio": stock_df["norm_dist_of_ratio"].iloc[0]
     }
    }
    
    trades_data.append(trade_details)
    
    
def trade_long_rebalance_entry(trades_data, stock_df, flag, buy_stock, sell_stock):
    for trade in trades_data:
        if trade["trade_close"] == False:
            trade["rebalance_buy"] = {"stock_name": buy_stock, 
                "date": stock_df["DATE"].iloc[0],
                "sell_price": stock_df[buy_stock].iloc[0],
                "quatity": STOCK_A_LOT_SIZE,
                "amount": stock_df[buy_stock].iloc[0] * STOCK_A_LOT_SIZE,
                "ratio": stock_df["ratio"].iloc[0],
                "norm_dist_of_ratio": stock_df["norm_dist_of_ratio"].iloc[0],
                "flag": flag
            }
        
            trade["rebalance_sell"] = {"stock_name": sell_stock, 
                "date": stock_df["DATE"].iloc[0],
                "buy_price": stock_df[sell_stock].iloc[0],
                "quatity": STOCK_B_LOT_SIZE,
                "amount": stock_df[sell_stock].iloc[0] * STOCK_B_LOT_SIZE,
                "ratio": stock_df["ratio"].iloc[0],
                "norm_dist_of_ratio": stock_df["norm_dist_of_ratio"].iloc[0],
                "flag": flag
            }
        
            stock_a_pl = trade["rebalance_buy"]['amount'] -  trade["buy"]["amount"]
            stock_b_pl = trade["rebalance_sell"]['amount'] -  trade["sell"]["amount"]
        
            trade["trade_description"] = {
                "stock_A_profit_loss" : stock_a_pl,
                "stock_B_profit_loss": stock_b_pl,
                "total_profit": stock_a_pl + stock_b_pl,
                "flag": flag
            }
        
            trade["trade_close"] = True
            
    
def check_trigger_condition_for_long(stock_df):
    return stock_df['norm_dist_of_ratio'].between(LONG_TRIGGER_MIN, LONG_TRIGGER_MAX).any()
    

def check_trigger_condition_for_long_target(stock_df):
    #return (stock_df['norm_dist_of_ratio'] <= LONG_TRIGGER_TARGET).any()
    return stock_df['norm_dist_of_ratio'].between(LONG_TRIGGER_TARGET_MIN, LONG_TRIGGER_TARGET_MAX).any()

def check_trigger_condition_for_long_stoploss(stock_df):
    #return (stock_df['norm_dist_of_ratio'] >= LONG_TRIGGER_STOPLOSS).any() 
    return stock_df['norm_dist_of_ratio'].between(LONG_TRIGGER_STOPLOSS_MIN, LONG_TRIGGER_STOPLOSS_MAX).any()


def check_trigger_condition_for_short(stock_df):
    return stock_df['norm_dist_of_ratio'].between(SHORT_TRIGGER_MIN, SHORT_TRIGGER_MAX).any()
    

def check_trigger_condition_for_short_target(stock_df):
    return (stock_df['norm_dist_of_ratio'] <= SHORT_TRIGGER_TARGET).any()


def check_trigger_condition_for_short_stoploss(stock_df):
    return (stock_df['norm_dist_of_ratio'] >= SHORT_TRIGGER_STOPLOSS).any()
    

# start 
stock_df = st.api_get_pair_trading_data(START_DATE, END_DATE).tail(1)  # check last day details


# check long trade first
if check_trigger_condition_for_long(stock_df):
    trade_long_entry(stock_df, buy_stock=TRADE_A_STOCK, sell_stock=TRADE_B_STOCK, trade_flag=LONG_TRADE_FLAG)
    
   
past_entry_date = END_DATE  

# for long trade
for day in tqdm(range(stop_itr)):  

    # buy & sell trade
    new_end_date = END_DATE + timedelta(days=day+1)  # get new date for fetching data
    
    stock_df = st.api_get_pair_trading_data(START_DATE, new_end_date).tail(1)  # get last entry 
    
    # if any holiday or weekends, skip those dates
    if past_entry_date == stock_df["DATE"].iloc[0]:
        continue
    
    past_entry_date = stock_df["DATE"].iloc[0]  # update past date
   
    # condition for the long entry 
    # if condition satisfied, then make entry 
    if check_trigger_condition_for_long(stock_df):
        trade_long_entry(stock_df, buy_stock=TRADE_A_STOCK, sell_stock=TRADE_B_STOCK, trade_flag=LONG_TRADE_FLAG)
        
    # rebalance the long trade (target and stoploss)
    if check_trigger_condition_for_long_target(stock_df):  # target
        trade_long_rebalance_entry(trades_data, stock_df, TARGET_FLAG, buy_stock=TRADE_A_STOCK, sell_stock=TRADE_B_STOCK)
        
        
    if check_trigger_condition_for_long_stoploss(stock_df):  # stoploss
        trade_long_rebalance_entry(trades_data, stock_df, STOPLOSS_FLAG, buy_stock=TRADE_A_STOCK, sell_stock=TRADE_B_STOCK)
        
    
    # condtion for the short entry
    if check_trigger_condition_for_short(stock_df):
        trade_long_entry(stock_df, buy_stock=TRADE_B_STOCK, sell_stock=TRADE_A_STOCK, trade_flag=SHORT_TRADE_FLAG)
        
    # rebalance the long trade (target and stoploss)
    if check_trigger_condition_for_short_target(stock_df):  # target short
        trade_long_rebalance_entry(trades_data, stock_df, TARGET_FLAG, buy_stock=TRADE_B_STOCK, sell_stock=TRADE_A_STOCK)
        continue
        
    if check_trigger_condition_for_short_stoploss(stock_df):  # stoploss short
        trade_long_rebalance_entry(trades_data, stock_df, STOPLOSS_FLAG, buy_stock=TRADE_B_STOCK, sell_stock=TRADE_A_STOCK)
        

print("Total Trades:", len(trades_data))  # print total number of trades

#print(trades_data)
        
# ----------------------------------------
trade_date = []
trade_ratio = []

trade_re_date = []
trade_re_ratio = []

sells_count = 0 
sells_target_count = 0
sells_stoploss_count = 0


for i in trades_data:
    trade_date.append(i["buy"]["date"])
    trade_ratio.append(i["buy"]["ratio"])
    
    if i["trade_close"]:
        trade_re_date.append(i["rebalance_buy"]["date"])
        trade_re_ratio.append(i["rebalance_buy"]["ratio"])
        sells_count = sells_count + 1
        
        if i["rebalance_buy"]["flag"] == TARGET_FLAG:
            sells_target_count = sells_target_count + 1
            
        if i["rebalance_buy"]["flag"] == STOPLOSS_FLAG:
            sells_stoploss_count = sells_stoploss_count + 1

print("Number stock Sells: ", sells_count)
print("Number stock Target Sells: ", sells_target_count)
print("Number stock Stoploss Sells: ", sells_stoploss_count)

all_stock_df = st.api_get_pair_trading_data(START_DATE, STOP_DATE)

mean_ratio = all_stock_df['ratio'].mean()


# plot diagram
plt.figure(figsize=(8, 5))

sns.lineplot(x=all_stock_df['DATE'], y=all_stock_df['ratio'], label="Ratio")

plt.axhline(y=mean_ratio, color="green", label="Mean of ratio")

plt.scatter(x=trade_date, y=trade_ratio, c="red")  # plot long
plt.scatter(x=trade_re_date, y=trade_re_ratio, c="yellow")  # plot long

#  Add titles and labels
plt.title("Ratio")
plt.xlabel("Index")
plt.ylabel("Values / Ratio")
plt.legend()

# Show the plot
plt.show()
