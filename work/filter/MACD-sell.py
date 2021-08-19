import pandas as pd
import numpy as np
import talib

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# print(sys.path)
import okap


# input_fname  = "stock-code-list/8man-12man-volume-over40k.txt"
input_fname  = "stock-code-list/buy-list.txt"
output_fname = "stock-code-list/filterMACD.txt"
 
year  = 2021
years = [2021,2020]
# codes = [2151]
# codes = okap.read_stock_code_list(input_fname)
df_buy_list = pd.read_csv("stock-code-list/buy-list.txt")

code_list = []

tmp_message = "===========================\nMACD sell\n==========================="
print(tmp_message)

message_list = []

for date, code in zip(df_buy_list["Date"], df_buy_list["code"]):

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

    # MACDを求める
    macd_period1 = 12
    macd_period2 = 26
    macd_period3 = 9

    if not macd_period1:
        macd_period1 = 12
    if not macd_period2:
        macd_period2 = 26
    if not macd_period3:
        macd_period3 = 9

    if macd_period1 is not None:
        macd, macd_signal, macd_hist = talib.MACD(np.asarray(df.Close, dtype='float64'), fastperiod=int(macd_period1), slowperiod=int(macd_period2), signalperiod=int(macd_period3))
        macd[np.isnan(macd)] = 0
        macd_signal[np.isnan(macd_signal)] = 0
        macd_hist[np.isnan(macd_hist)] = 0
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        df['macd_hist'] = macd_hist
    
    # print(df)
    
    df_new = pd.DataFrame(index=df.index, columns=[])
    df_new['macd'] = df.macd
    df_new['macd_signal'] = df.macd_signal
    df_new['macd_hist'] = df.macd_hist


    # 終値を一日シフトさせる 
    okap.make_x_day_shift(df_new,"macd_hist", 1, "macd_hist_1day_ago")

    row = df_new[-1:]

    # 移動平均が終値より高い＆高値が移動平均を超えている＆終値が始値より高い
    tmp_text = ""
    if (row["macd"].values < 0):
        if (row["macd_hist"].values < 0):
            tmp_text = "{:4}: {}, {}".format(code, "macd -", "macd hist -")
        else:
            tmp_text = "{:4}: {}, {}".format(code, "macd -", "macd hist +")
        code_list.append(tmp_text)
        print("HIT: ------------------------> ", code)

print("==== MACD sell list ====")
for x in code_list:
    print(x)
