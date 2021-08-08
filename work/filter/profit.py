import pandas as pd
import numpy as np
import talib
import datetime

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
codes = okap.read_stock_code_list(input_fname)

code_list = []

# hit_message = "====================\nおすすめの株\n8万以上12万以下\n2日連続で陽線\n5日移動平均線が上昇\n===========================\n"
hit_message = "====================\nprofit\n===========================\n"
print(hit_message)
message_list = []
total = 0
plus_list = []
minus_list =[]
for code in codes:

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
        continue

    # print(df['Date'])
    # 日付を文字列 year/month/day からdatetime(unix時間)に変換
    # print(pd.to_datetime(df["Date"]))
    buy_date = datetime.datetime(2021,8,2,22,30,0, tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
    # print(buy_date)
    buy_price = df[pd.to_datetime(df["Date"]) == buy_date].Close.values
 
    # 終値を一日シフトさせる 
    okap.make_x_day_shift(df,"Close", 1, "Close_1day_ago")

    row = df[-1:]

    # profit = row["Close"].values - row["Close_1day_ago"].values
    # print(code, " profit: ", profit, " : ",  row["Close"].values, row["Close_1day_ago"].values)

    profit = row["Close"].values - buy_price
    tmp_text = code.ljust(5) + "profit: " + str(profit) + " : " + str(row["Close"].values) + str(buy_price)
    # print(tmp_text)
    if profit > 0:
        plus_list.append(tmp_text)
    else:
        minus_list.append(tmp_text)
 
    total += profit

print("==== plus ====")
for x in plus_list:
    print(x)
print("==== minus ====")
for x in minus_list:
    print(x)
print("==== total ====")
print(total)

    # 移動平均が終値より高い＆高値が移動平均を超えている＆終値が始値より高い

    # print("END:  ", code)
    #for index, row in df_new.iterrows():
    #    if(row['2day_positive'] == true and row["2day_colse_goes_up"] == true and row['1day_sma_goes_up'] == true):
    #        print(index)
# with open(output_fname, 'wt') as f:
#     for code in code_list:
#         f.write(str(code)+'\n')
# 
# print("total: ", total)
# 
# print("以下おすすめの株です")
# if len(hit_message + "\n===========================\n") > 1000:
#     message_list.append(hit_message)
#     message_list.append("\n===========================\n")
# else:
#     hit_message = hit_message + "\n===========================\n"
#     message_list.append(hit_message)
#     
# for message in message_list:
#     print(message)
#     # send_message(message)

# return {
#     'statusCode': 200,
#     'body': json.dumps('Hello from Lambda!')
# }
