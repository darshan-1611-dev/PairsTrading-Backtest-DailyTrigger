import pymongo
from datetime import date, timedelta, datetime
from jugaad_data.nse import stock_df
from tqdm import tqdm
from joblib import Memory

memory = Memory(location="D:/Darshan's Projects/The pair trading/cachedir", verbose=0)


CONNECTION_STRING = "mongodb://localhost:27017/"
CURRENT_DATABASE = "pairTradingDB"
CURRENT_COLLECTION = "allStockDataCollection"

# Dates for download stock price in range
START_DATE = datetime(2000,1,1)  # YYYY-MM-DD 
END_DATE =  datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

def connect_to_db():
    myclient = pymongo.MongoClient(CONNECTION_STRING)  # connect to the mongoDB
    
    db = myclient[CURRENT_DATABASE]  # connect to the Database
    
    global collection
    collection = db[CURRENT_COLLECTION]  # connect to the Collection
    

def collect_and_insert_data(stock_symbol, start_date=START_DATE, end_date=END_DATE):
    try:
        if stock_symbol and start_date and end_date:
            # fetch data of stocks
            df = stock_df(symbol=stock_symbol, from_date=start_date.date(),
                to_date=end_date.date(), series="EQ")
            
            df["STOCK_SYMBOL"] = stock_symbol # add symbol to column
            
            # Convert DataFrame to list of dictionaries
            transformed_data = df.to_dict(orient='records')
            
            #insert data to the database
            collection.insert_many(transformed_data)
     
    except Exception as e:
        print("------------------ ERROR --------------------------")
        print("Error:", stock_symbol)
        print(e)
        print("---------------------------------------------------")
        
        
def refresh_stock_price(stock_symbol):  
    getLatest_date = list(collection.find({"STOCK_SYMBOL": stock_symbol}, {'DATE': 1, '_id': 0}).sort("DATE", -1).limit(1))[0]["DATE"]
   
    # if stock updaetd till current date then retrun
    if getLatest_date == END_DATE: 
        print(f"Updated until ({getLatest_date.date()})': {stock_symbol}")
        return 
    
    start_date = getLatest_date + timedelta(days=1)
    # update new data to the table
    collect_and_insert_data(stock_symbol, start_date=start_date)  
    print("Update: ", stock_symbol)


def is_stock_symbol_in_db(stock_symbol):
    count_data =  collection.count_documents({"STOCK_SYMBOL": stock_symbol})
    return count_data > 0 # if raw count more than 0, return True Otherwise False
    
 
'''
 This is function is uses to getting a stock details.
 parameters:
    stock_symbol (ex: "ADANIGREEN")
    start_date (ex: datetime(2000,1,1)) YYYY-MM-DD 
    end_date (ex: datetime(2020,12,4)) YYYY-MM-DD 
'''
def get_stock_details(stock_symbol, start_date=START_DATE, end_date=END_DATE):
    stock_data = []

    if stock_symbol:
        stock_data = list(collection.aggregate([
    {"$match": {  
        "STOCK_SYMBOL": stock_symbol,  
        "DATE": {"$gte": start_date, "$lte": end_date}  
    }},
    {"$sort": {"DATE": 1}}  # Sort by DATE in ascending order
]))
            
    return stock_data
   
   
if __name__ == "__main__":

    # connect to the database
    connect_to_db()

    # read stock symbol data from file 
    stock_symbol_list = open('stock_symbol.txt','r').readlines()


    '''
    check every stock from file `stock_symbol.txt` and if stock alredy exist in database than it  will be update the stock price with the current date and if not than insert new data. 
    '''
    for stock in stock_symbol_list:
        if stock:
            stock = stock.strip()
            if is_stock_symbol_in_db(stock):
                refresh_stock_price(stock)
            else:
                collect_and_insert_data(stock) 
                print("Insert: ", stock)


