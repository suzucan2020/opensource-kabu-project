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

macd_list = []
macd_sell_list = []
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

    # カラムごとの計算手法を指定
    agg_dict = {
        "Open": "first", 
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    }


    tmp_text = "code: {:6} ".format(code)
    for x in ["day", "Week", "Month"]:
        # print(x)
        if x == "day":
            macd_period1 = 12
            macd_period2 = 26
            macd_period3 = 9
            df_new = df
            # print(df_new)
        elif x == "Week":
            macd_period1 = 9
            macd_period2 = 20
            macd_period3 = 4
            datetime_tmp = pd.to_datetime(df["Date"])
            df_new = df.drop(columns='Date')
            df_new = df_new.set_index(datetime_tmp).resample('W').agg(agg_dict)
            # print(df_new)
        else:
            macd_period1 = 12
            macd_period2 = 24
            macd_period3 = 6
            datetime_tmp = pd.to_datetime(df["Date"])
            df_new = df.drop(columns='Date')
            df_new = df_new.set_index(datetime_tmp).resample('M').agg(agg_dict)
            # print(df_new)

        if macd_period1 is not None:
            macd, macd_signal, macd_hist = talib.MACD(np.asarray(df_new.Close, dtype='float64'), fastperiod=int(macd_period1), slowperiod=int(macd_period2), signalperiod=int(macd_period3))
            macd[np.isnan(macd)] = 0
            macd_signal[np.isnan(macd_signal)] = 0
            macd_hist[np.isnan(macd_hist)] = 0
            df_new['macd'] = macd
            df_new['macd_signal'] = macd_signal
            df_new['macd_hist'] = macd_hist
        
        # print(df_new)
        

        # 終値を一日シフトさせる 
        okap.make_x_day_shift(df_new,"macd_hist", 1, "macd_hist_1day_ago")

        row = df_new[-1:]

        # 移動平均が終値より高い＆高値が移動平均を超えている＆終値が始値より高い
        # if (row["macd"].values < 0):
        #     if (row["macd_hist"].values < 0):
        #         tmp_text += " {:>5}: {} {}".format(x, "macd -", "hist -")
        #     else:
        #         tmp_text += " {:>5}: {} {}".format(x, "macd -", "hist +")
        #     macd_sell_list.append(tmp_text)
        #     print("HIT: ------------------------> ", code)
        # else:
        #     if (row["macd_hist"].values < 0):
        #         tmp_text += " {:>5}: {} {}".format(x, "macd +", "hist -")
        #     else:
        #         tmp_text += " {:>5}: {} {}".format(x, "macd +", "hist +")
        if (row["macd_hist"].values < 0):
            if (row["macd"].values < 0):
                tmp_text += "{:>5}: {} {} , ".format(x, "macd -", "hist -")
            else:
                tmp_text += "{:>5}: {} {} , ".format(x, "macd +", "hist -")
            macd_sell_list.append(tmp_text)
            # print("HIT: ------------------------> ", code)
        else:
            if (row["macd"].values < 0):
                tmp_text += "{:>5}: {} {} , ".format(x, "macd -", "hist +")
            else:
                tmp_text += "{:>5}: {} {} , ".format(x, "macd +", "hist +")
    macd_list.append(tmp_text)
    # print(tmp_text)

print("==== MACD list ====")
for x in macd_list:
    print(x)

print("==== MACD sell list ====")
for x in macd_sell_list:
    print(x)
