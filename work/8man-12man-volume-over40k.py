# import json

import urllib.request
import datetime
import time

# import boto3
# import botocore
# from botocore.exceptions import ClientError

import os
import pandas as pd

import okap

years = [2021]

# codes = [1301]
codes = okap.read_stock_code_list('stock-code-list/all.txt')

code_list = []
close_list = []
volume_list = []

msg = "対象銘柄入れ替え開始"
# send_message(msg)
print(msg)

for code in codes:
    for year in years:
        print("start: ", code)
        title = okap.read_title_form_s3(str(code), str(year))
        df = okap.read_df_from_s3(str(code), str(year))

        df = df.reindex(index=df.index[::-1])
        df.reset_index(inplace=True, drop=True)
        # print(df)
        if len(df) == 0:
            continue

        # 一番最近の終値、出来高、直近5日間の出来高の平均値を取り出す
        close = df.iloc[-1]["Close"]
        volume = df.iloc[-1]["Volume"]
        volume_mean = df["Volume"].rolling(window=5).mean()
        # print(volume_mean[-1:])
        # print(close)
        # フィルタ条件：一番最近の終値が800円以上1200以下、直近5日間の出来高の平均が40000以上
        if 800 <= close and close <= 1200 and volume_mean[-1:].values >= 40000:
            code_list.append(code)
            close_list.append(close)
            volume_list.append(volume_mean[-1:].values)
            print(title)
        print("end: ", title)

df2 = pd.DataFrame(
data={'Close': close_list, 'Volume': volume_list},
index=code_list,
columns=['Close', 'Volume']
)
print(df2)
# df2.to_csv('s3://kabu-data/target_code.csv', index_label='code')

with open("stock-code-list/8man-12man-volume-over40k.txt", 'wt') as f:
    for code in code_list:
        f.write(str(code)+'\n')

msg = "対象銘柄入れ替え完了"
# send_message(msg)
print(msg)        
# return {
#     'statusCode': 200,
#     'body': json.dumps('Hello from Lambda!'),
#     }
