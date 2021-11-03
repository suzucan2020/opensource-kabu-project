import pandas as pd
import numpy as np
import talib

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# print(sys.path)
import okap


# input_fname  = "stock-code-list/8man-12man-volume-over40k.txt"
input_fname  = "stock-code-list/all.txt"
output_fname = "stock-code-list/MACD-over-0.txt"
 
year  = 2021
years = [2021,2020]
# codes = [2151]
codes = okap.read_stock_code_list(input_fname)

code_list = []

# hit_message = "====================\nおすすめの株\n8万以上12万以下\n2日連続で陽線\n5日移動平均線が上昇\n===========================\n"
hit_message = "\
===========================\n\
おすすめの株\nMACDが0越え\n\
===========================\n\
"
message_list = []
for code in codes:

    print("START: ", code)
    # title = okap.read_title_form_s3(str(code), str(year))
    title = str(code)
    # print(title)
    df = okap.read_df_from_s3(str(code), str(year))
    # if not os.path.isfile(file_name):
    #    print("file not exist: ", file_name)
    #    continue
    # df = df.reindex(index=df.index[::-1])
    # df.reset_index(inplace=True, drop=True)
    # print(code)
    # print(df)
    if len(df) == 0:
        continue


    # カラムごとの計算手法を指定
    agg_dict = {
        "Open": "first", 
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    }

    # print(df)
    datetime_tmp = pd.to_datetime(df["Date"])
    df = df.drop(columns='Date')
    df = df.set_index(datetime_tmp).resample('M').agg(agg_dict)
 
    # MACDを求める
    macd_period1 = 12
    macd_period2 = 24
    macd_period3 = 6

    if macd_period1 is not None:
        macd, macd_signal, macd_hist = talib.MACD(np.asarray(df.Close, dtype='float64'), fastperiod=int(macd_period1), slowperiod=int(macd_period2), signalperiod=int(macd_period3))
        macd[np.isnan(macd)] = 0
        macd_signal[np.isnan(macd_signal)] = 0
        macd_hist[np.isnan(macd_hist)] = 0
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        df['macd_hist'] = macd_hist

    max_count = 0
    tmp_count = 0
    tmp_str = ""
    max_str = ""
    for index, row in df.iterrows():
        # print(index, row['Date'], row['macd'])
        if row['macd'] > 0:
            if tmp_count == 0:
                tmp_str = "code: {:6} start: {} ".format(code, index.strftime("%Y-%m-%d"))
                buy_close = row["Close"]
            tmp_count += 1
        else:
            tmp_count = 0

        if tmp_count > max_count:
            max_count = tmp_count
            profit = (row["Close"] - buy_close) / buy_close * 100
            max_str = tmp_str + "end: {} max_count: {:3} Close: {:6.1f} buy: {:6.1f} profit: {:6.1f}".format(index.strftime("%Y-%m-%d"), max_count, row["Close"], buy_close, profit)

    print(max_str)
