import pandas as pd 
import database as db
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm, gaussian_kde
import numpy as np

db.connect_to_db()  # connect to the database 

STOCK_A_SYMBOL = "AXISBANK"                     
STOCK_B_SYMBOL = "ICICIBANK" 


START_DATE = datetime(2015, 12, 4)                  
END_DATE = datetime(2017, 12, 4)

'''
START_DATE = datetime(2022, 1, 1)                  
END_DATE = datetime(2025, 3, 11)
'''

# calculate ratio of two stocks 
# ratio =STOCk A/STOCK B 
def calculate_ratio_with_mean_median_and_mode(stock_df):
    ratio = round(stock_df[STOCK_A_SYMBOL] / stock_df[STOCK_B_SYMBOL], 3)
  
    mean = ratio.mean()  # calculate mean
    std = ratio.std()  # calculate std
  
    norm_dist_of_ratio = norm.cdf(ratio, loc=mean, scale=std)  # calculate norm dist of ratio
    
    description = {
    "ratio": ratio,
    "norm_dist_of_ratio": norm_dist_of_ratio,
    "mean": mean,
    "median": ratio.median(),
    "mode": ratio.mode()[0],
    "std": std,
    "first_sd_above_mean": mean + std,
    "second_sd_above_mean": mean + 2 * std,
    "third_sd_above_mean": mean + 3 * std,
    "first_sd_below_mean": mean - std,
    "second_sd_below_mean": mean - 2 * std,
    "third_sd_below_mean": mean - 3 * std
    }
    return description
    

def api_get_pair_trading_data(start_date, end_date):
    stock_A_data = pd.DataFrame(db.get_stock_details(STOCK_A_SYMBOL, start_date=start_date, end_date=end_date))
    
    stock_B_data = pd.DataFrame(db.get_stock_details(STOCK_B_SYMBOL, start_date=start_date, end_date=end_date))
    
    stock_df = pd.DataFrame({"DATE": stock_A_data["DATE"], STOCK_A_SYMBOL: stock_A_data['CLOSE'], STOCK_B_SYMBOL: stock_B_data['CLOSE']})
    
    ratio_description = calculate_ratio_with_mean_median_and_mode(stock_df)
    
    stock_df['ratio'] =  ratio_description['ratio']  # add ratio to df
    stock_df['norm_dist_of_ratio'] =  ratio_description['norm_dist_of_ratio']  # add norm dist of ratio to df
    
    return stock_df
    

if __name__ == "__main__":
    stock_A_data = pd.DataFrame(db.get_stock_details(STOCK_A_SYMBOL, start_date=START_DATE, end_date=END_DATE))
    stock_B_data = pd.DataFrame(db.get_stock_details(STOCK_B_SYMBOL, start_date=START_DATE, end_date=END_DATE))

    stock_df = pd.DataFrame({"DATE": stock_A_data["DATE"], STOCK_A_SYMBOL: stock_A_data['CLOSE'], STOCK_B_SYMBOL: stock_B_data['CLOSE']})

    ratio_description = calculate_ratio_with_mean_median_and_mode(stock_df)

    stock_df['ratio'] =  ratio_description['ratio']  # add ratio to df
    stock_df['norm_dist_of_ratio'] =  ratio_description['norm_dist_of_ratio']  # add norm dist of ratio to df
    

    filtered_df_long = stock_df[(stock_df['norm_dist_of_ratio'] > 0.003) & (stock_df['norm_dist_of_ratio'] < 0.025)]


    filtered_df_short = stock_df[(stock_df['norm_dist_of_ratio'] > 0.975) & (stock_df['norm_dist_of_ratio'] < 0.997)]



    # Plot the ratio column
    plt.figure(figsize=(8, 5))

    sns.lineplot(x=stock_df['DATE'], y=stock_df['ratio'], label="Ratio")

    plt.axhline(y=ratio_description["mean"], color="green", label="Mean of ratio")

    plt.scatter(x=filtered_df_long['DATE'], y=filtered_df_long['ratio'], c="red")  # plot long
    plt.scatter(x=filtered_df_short['DATE'], y=filtered_df_short['ratio'], c="green")  # plot short

    #  Add titles and labels
    plt.title("Ratio")
    plt.xlabel("Index")
    plt.ylabel("Values / Ratio")
    plt.legend()

    # Show the plot
    plt.show()
