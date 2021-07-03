import pandas as pd
import numpy as np
import talib


import sys
import urllib.parse
import urllib.request
import os

# s3から株価データを取り出し、銘柄を抜き出す
def read_title_form_s3(stock_code, selected_year):
    # file_name = "s3://kabu-data/" + stock_code + "_" + selected_year + ".csv"
    file_name = stock_code + "_" + selected_year + ".csv"
    title = pd.read_csv(file_name, nrows=1, encoding="shift-jis")
    title = title.columns[0]
    return title

# s3から株価データを取り出し、データをdataframeに落とし込む
def read_df_from_s3(stock_code, selected_year):
    # file_name = "s3://kabu-data/" + stock_code + "_" + selected_year + ".csv"
    file_name = stock_code + "_" + selected_year + ".csv"
    df = pd.read_csv(file_name, header=1, encoding="shift-jis")
    # df = pd.read_csv(file_name, encoding="shift-jis")
    df.columns = ["Date", "Open", "High", "Low", "Close", "Volume", "Trading Value"]
    df = df.dropna()
    df = df.astype({"Open": float, "High": float, "Low": float, "Close": float, "Volume": float, "Trading Value": float})
    return df

# シフト関数
# 引数：dataframe、シフトさせるカラム、何日シフトするか、新しいカラム名
def make_x_day_shift(df, shift_column_name, x, new_column_name):
    roll_date = np.roll(df[shift_column_name], x)
    # シフトした部分はinfとする、後々の判定に使用する際にinfとしておけば正しく判定できるため
    roll_date[0:x] = float('inf')
    roll_date[( roll_date == 0)] = float('inf')
    df[new_column_name] = roll_date

# 比較関数
def make_compare_column(df, column_name1, column_name2, new_column_name):
    df[new_column_name] = ( df[column_name1] > df[column_name2] )

# ｘ日上昇が続いているか判定関数
def judge_x_days_goes_up(df, column_name, x, new_column_name):
    tmp_list = []
    for i in range(len(df)):
        if i < x -1:
            tmp_list.append(False)
        else:
            tmp_list.append(np.all( df[i+1-x:i+1][column_name] ))
    df[new_column_name] = tmp_list

year  = 2021
years = [2021]
codes = [
"9468"
]

# hit_message = "====================\nおすすめの株\n8万以上12万以下\n2日連続で陽線\n5日移動平均線が上昇\n===========================\n"
hit_message = "====================\nおすすめの株\n8万以上12万以下\n終値が移動平均線より低い＆高値が移動平均線を超えている\n===========================\n"
message_list = []
for code in codes:

    title = read_title_form_s3(str(code), str(year))
    # print(title)
    df = read_df_from_s3(str(code), str(year))
    # if not os.path.isfile(file_name):
    #    print("file not exist: ", file_name)
    #    continue
   
    # # talib$Onparray$K$9$k.7?$Odouble$K$9$k
    # 5日移動平均を求める
    sma = talib.SMA(np.asarray(df.Close, dtype='float64'), 5)
    # nanデータは0とする
    sma[np.isnan(sma)] = 0.0
    # print(sma)
    df['sma'] = sma

    df_new = pd.DataFrame(index=df.index, columns=[])
    df_new["Open"] = df.Open
    df_new["Close"] = df.Close
    df_new["High"] = df.High
    # df_new["diff"] = (df.Close - df.Open)

    # 終値が始値より高いか
    make_compare_column(df_new, "Close", "Open", "today_positive")
    # 二日連続で上昇しているかどうか
    judge_x_days_goes_up(df_new, "today_positive", 2, "2day_positive")

    # 終値を一日シフトさせる 
    make_x_day_shift(df_new,"Close", 1, "Close_1day_ago")
    # 今日の終値は昨日の終値より高いかどうか
    make_compare_column(df_new, "Close", "Close_1day_ago", "1day_Colse_goes_up")
    # 2日連続で終値が上昇しているかどうか
    judge_x_days_goes_up(df_new, "1day_Colse_goes_up", 2, "2day_Colse_goes_up")

    df_new['sma'] = df.sma
    # 移動平均を1日シフト
    make_x_day_shift(df_new, "sma", 1, "sma_1day_ago")
    # 移動平均が昨日より高いかどうか
    make_compare_column(df_new, "sma", "sma_1day_ago", "1day_sma_goes_up")


    # pd.set_option('display.max_rows', 500)
    # print(df_new)
    # print(df_new["today_positive"].value_counts())

    row = df_new[-1:]
    #if (row['2day_positive'].all() == True) and (row["2day_Colse_goes_up"].all() == True) and (row['1day_sma_goes_up'].all() == True):
    #    tmp_title = title[:20]
    #    print(tmp_title)
    #    if len(hit_message + tmp_title + "\n") > 1000:
    #        message_list.append(hit_message)
    #        hit_message = "\n" + tmp_title + "\n"
    #    else:
    #        hit_message = hit_message + tmp_title + "\n"
    # print(row["Close"].values)
   
    # 移動平均が終値より高い＆高値が移動平均を超えている＆終値が始値より高い
    if (row["Close"].values <= row["sma"].values) & (row["sma"].values <= row["High"].values) & (row["Close"].values > row["Open"].values):
        tmp_title = title[:20]
        print(tmp_title)
        if len(hit_message + tmp_title + "\n") > 1000:
            message_list.append(hit_message)
            hit_message = "\n" + tmp_title + "\n"
        else:
            hit_message = hit_message + tmp_title + "\n"
        

    #for index, row in df_new.iterrows():
    #    if(row['2day_positive'] == true and row["2day_colse_goes_up"] == true and row['1day_sma_goes_up'] == true):
    #        print(index)

print("以下おすすめの株です")
if len(hit_message + "\n===========================\n") > 1000:
    message_list.append(hit_message)
    message_list.append("\n===========================\n")
else:
    hit_message = hit_message + "\n===========================\n"
    message_list.append(hit_message)
    
for message in message_list:
    print(message)
    # send_message(message)

# return {
#     'statusCode': 200,
#     'body': json.dumps('Hello from Lambda!')
# }
