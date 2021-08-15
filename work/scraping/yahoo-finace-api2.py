from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import pandas as pd

# data_list = [ \
#     ["4391.T", "LOGIZARD"], 
#     ["4755.T", "RAKUTEN"],
#     ["2303.T", "DAWN"]]

import time

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# print(sys.path)
import okap

# codes = [1301]
# codes = okap.read_stock_code_list('stock-code-list/all.txt')
# codes = okap.read_stock_code_list('stock-code-list/buy-list.txt')
df_codes = pd.read_csv("stock-code-list/buy-list.txt")
codes = df_codes["code"]

# codes = [
#        "BEST",
#        "BF.A",
#        "BF.B"
#        ]

start_time = time.time()

tmp_message = "===========================\nscraping\n==========================="
print(tmp_message)
for i, code in enumerate(codes):
    # company_code = str(code) + ".T"
    company_code = code
    my_share = share.Share(company_code)

    
    print("START: ", company_code)
    try:
        # symbol_data = my_share.get_historical(share.PERIOD_TYPE_WEEK, 1000,
        symbol_data = my_share.get_historical(share.PERIOD_TYPE_WEEK, 100,
                                        share.FREQUENCY_TYPE_DAY, 1)
        # print(symbol_data)
        if symbol_data == None:
            print("symbol_data == None")
            continue

        df = pd.DataFrame(symbol_data.values(), index=symbol_data.keys()).T
        df.timestamp = pd.to_datetime(df.timestamp, unit='ms')
        df.index = pd.DatetimeIndex(df.timestamp, name='Date').tz_localize('UTC').tz_convert('Asia/Tokyo')
        
        df["Trading Value"] = df.close
        df = df.drop('timestamp', axis='columns')
        df = df.set_axis(['Open','High','Low','Close','Volume','Trading Value'], axis='columns')

        # print(df)
        df.to_csv("kabu-data/"+str(code)+"_2021.csv")
        spend_time = time.time() - start_time
        print("END:   ", spend_time)
        print("-")

    except YahooFinanceError as e:
        print(e.message)
        pass
