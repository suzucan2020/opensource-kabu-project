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
# codes = ["MAIN"]
codes = okap.read_stock_code_list(input_fname)

code_list = []

# hit_message = "====================\nおすすめの株\n8万以上12万以下\n2日連続で陽線\n5日移動平均線が上昇\n===========================\n"
# hit_message = "\
# ===========================\n\
# おすすめの株\nMACDが0越え\n\
# ===========================\n\
# "
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
    #print(df)

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
    
    # print(df)
    
    # macdを一日シフトさせる 
    okap.make_x_day_shift(df,"macd", 1, "macd_1day_ago")
    okap.make_x_day_shift(df,"macd_hist", 1, "macd_hist_1day_ago")

    macd_plus_count = 0
    for index, row in df.iterrows():
        # print("{} {:>7.2f} {} {}".format( index.strftime("%Y-%m-%d"), row["Close"], row["macd"], row["macd_signal"] ) )
        if (row["macd"] > 0):
            if (macd_plus_count == 0):
                tmp_str = "BUY: {} {:>7.2f}".format( index.strftime("%Y-%m-%d"), row["Close"] )
                buy_close = row["Close"]
            macd_plus_count += 1
        else:
            if (macd_plus_count > 0):
                profit = row["Close"] / buy_close
                tmp_str = "Trade --> code: {:6} ".format( code ) + tmp_str + " SELL: {} {:>7.2f}  macd: {:>7.2f} macd_count: {:>3} profit: {:>5.2f}".format( index.strftime("%Y-%m-%d"), row["Close"], row["macd"], macd_plus_count, profit )
                print(tmp_str)
            macd_plus_count = 0
    if (macd_plus_count > 0):
        profit = row["Close"] / buy_close
        tmp_str = "Trade --> code: {:6} ".format( code ) + tmp_str + " SELL: {} {:>7.2f}  macd: {:>7.2f} macd_count: {:>3} profit: {:>5.2f}".format( index.strftime("%Y-%m-%d"), row["Close"], row["macd"], macd_plus_count, profit )
        print(tmp_str)

#     row = df[-1:]
#     profit = df[-1:]["Close"].values[0] / df[:1]["Close"].values[0]
#     # print(profit)
#     
#     macd_plus = df[df["macd"] > 0]
#     print("HIT: ------------------------> code: {:6} close: {:>7.2f} macd: {:>7.2f} macd: count: {:>5} profit: {:>7.2f}".format(code, row["Close"].values[0], row["macd"].values[0], macd_plus["macd"].count(), profit) )
#
#    # 移動平均が終値より高い＆高値が移動平均を超えている＆終値が始値より高い
#    # if (row["macd"].values > 0) & (row["macd_1day_ago"].values <= 0):
#    if (row["macd_hist"].values > 0) & (row["macd_hist_1day_ago"].values <= 0):
#    # if (row["macd"].values > 0):
#        code_list.append(code)
#        tmp_title = title[:20]
#        macd_plus = df[df["macd"] > 0]
#        print(macd_plus)
#        print(row["macd"].values[0])
#        print("HIT: ------------------------> {:6} {:>5.2f} {:>4}".format(tmp_title, row["macd"].values[0], macd_plus["macd"].count()) )
#        print(df)
#        # print(df)
#        if len(hit_message + tmp_title + "\n") > 1000:
#            message_list.append(hit_message)
#            hit_message = "\n" + tmp_title + "\n"
#        else:
#            hit_message = hit_message + tmp_title + "\n"

    print("END:  ", code)
