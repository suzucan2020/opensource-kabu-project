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
# codes = okap.read_stock_code_list(input_fname)
df_buy_list = pd.read_csv("stock-code-list/buy-list.txt")
# codes = df_buy_list["code"]

code_list = []

# hit_message = "====================\nおすすめの株\n8万以上12万以下\n2日連続で陽線\n5日移動平均線が上昇\n===========================\n"
hit_message = "===========================\nprofit\n==========================="
print(hit_message)
message_list = []
plus_list = []
plus_total = 0
plus_per_total = 0
minus_list =[]
minus_total = 0
minus_per_total = 0

np.set_printoptions(precision=2)
# for code in codes:
for date, code in zip(df_buy_list["Date"], df_buy_list["code"]):

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
    
    # MACD計算
    okap.calc_MACD(df)
    # print(df)

    # print(df['Date'])
    # 日付を文字列 year/month/day からdatetime(unix時間)に変換
    # print(pd.to_datetime(df["Date"]))
    # buy_date = datetime.datetime(2021,8,2,22,30,0, tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
    # print("buy_date: ", buy_date)
    # print("date:", date)
    buy_price = df[pd.to_datetime(df["Date"]) == date].Close.values

    row = df[-1:]

    # 利益計算
    profit = row["Close"].values - buy_price
    profit_per = (profit / buy_price)*100
    
    if (row["macd"].values < 0):
        text_macd = "{}".format("macd -")
    else:
        text_macd = "{}".format("macd +")

    if (row["macd_hist"].values < 0):
        text_macd_hist = "{}".format("macd hist -")
    else:
        text_macd_hist = "{}".format("macd hist +")


    
    tmp_text = code.ljust(5) +", " + text_macd + ", " + text_macd_hist + ", profit: " + str(profit).rjust(8) + ", per: " + str(profit_per).rjust(8) + ", now: " + str(row["Close"].values).rjust(8) + ", buy: " + str(buy_price).rjust(8)
    # print(tmp_text)
    if profit > 0:
        plus_list.append(tmp_text)
        plus_total += profit
        plus_per_total += profit_per
    else:
        minus_list.append(tmp_text)
        minus_total += profit
        minus_per_total += profit_per
 
print("==== plus ====")
for x in plus_list:
    print(x)
print("-")
print("     plus  len: ", len(plus_list))
tmp_text = "     profit: " + str(plus_total).rjust(8) + ", per: " + str(plus_per_total).rjust(8) + ", per/len(p): " + str(plus_per_total / len(plus_list)).rjust(8) + ", per/len(p+m): " + str(plus_per_total / (len(plus_list) + len(minus_list))).rjust(8)
print(tmp_text)
print("-")

print("==== minus ====")
for x in minus_list:
    print(x)
print("-")
print("     minus len: ", len(minus_list))
tmp_text = "     profit: " + str(minus_total).rjust(8) + ", per: " + str(minus_per_total).rjust(8) + ", per/len(m): " + str(minus_per_total / len(minus_list)).rjust(8) + ", per/len(p+m): " + str(minus_per_total / (len(plus_list) + len(minus_list))).rjust(8)
print(tmp_text)
print("-")

print("==== total ====")
# print(minus_total + plus_total,  ", ", minus_per_total + plus_per_total,  ", ", (minus_per_total + plus_per_total) / (len(plus_list) + len(minus_list)) )
tmp_text = "     profit: " + str(minus_total + plus_total).rjust(8) + ", per: " + str(minus_per_total + plus_per_total).rjust(8) + ", per/len(p+m): " + str((minus_per_total + plus_per_total) / (len(plus_list) + len(minus_list))).rjust(8)
print(tmp_text)



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
