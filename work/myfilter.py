import pandas as pd
import numpy as np
import talib

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# print(sys.path)
import okap

year  = 2021

def find_up_use_macd(code):
    
    # print("START: ", code)
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
        return 

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
    return_str = ""
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
                # print(tmp_str)
                return_str = return_str + tmp_str + "\n"
            macd_plus_count = 0
    if (macd_plus_count > 0):
        profit = row["Close"] / buy_close
        tmp_str = "Trade --> code: {:6} ".format( code ) + tmp_str + " SELL: {} {:>7.2f}  macd: {:>7.2f} macd_count: {:>3} profit: {:>5.2f}".format( index.strftime("%Y-%m-%d"), row["Close"], row["macd"], macd_plus_count, profit )
        # print(tmp_str)
        return_str = return_str + tmp_str + "\n"

    return return_str
    # print("END:  ", code)

def MACD_golden_cross(code):

    # print("START: ", code)
    
    title = str(code)
    
    df = okap.read_df_from_s3(str(code), str(year))
    
    if len(df) == 0:
        return

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

        if (row["macd"].values < 0):
            macd_str = "macd -"
        else:
            macd_str = "macd +"

        if (row["macd_hist"].values < 0):
            hist_str = "hist -"
        else:
            hist_str = "hist +"

        if (row["macd_hist_1day_ago"].values < 0):
            hist_1day_ago_str = "hist_1pre -"
        else:
            hist_1day_ago_str = "hist_1pre +"

        tmp_text += "{:>5}: {} {} {} , ".format(x, macd_str, hist_str, hist_1day_ago_str)

    return_str = ""
    # print(tmp_text)
    if "Week: macd + hist + hist_1pre - ," in tmp_text:
        # macd_list.append(tmp_text)
        # print(tmp_text)
        # print(find_up_use_macd(code))
        return_str = tmp_text + "\n" + find_up_use_macd(code)
    return return_str
 

