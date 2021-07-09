# import json

import urllib.request
import datetime
import time

# import boto3
# import botocore
# from botocore.exceptions import ClientError


import os
import pandas as pd

years = [2021]

codes = [
"9486"
]

# LINE notify's API
# LINE_TOKEN= os.environ.get("LINE_NOTIFY_API_KEY")
# LINE_NOTIFY_URL="https://notify-api.line.me/api/notify"
# def send_message(msg):
#     method = "POST"
#     headers = {"Authorization": "Bearer %s" % LINE_TOKEN}
#     payload = {"message": msg}
#     try:
#         payload = urllib.parse.urlencode(payload).encode("utf-8")
#         req = urllib.request.Request(
#             url=LINE_NOTIFY_URL, data=payload, method=method, headers=headers)
#         urllib.request.urlopen(req)
#     except Exception as e:
#         print ("Exception Error: ", e)
#         sys.exit(1)


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

code_list = []
close_list = []
volume_list = []

msg = "対象銘柄入れ替え開始"
# send_message(msg)
print(msg)

for code in codes:
    for year in years:
        print("start: ", code)
        title = read_title_form_s3(str(code), str(year))
        df = read_df_from_s3(str(code), str(year))

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

# df2 = pd.DataFrame(
# data={'Close': close_list, 'Volume': volume_list},
# index=code_list,
# columns=['Close', 'Volume']
# )
# print(df2)
# df2.to_csv('s3://kabu-data/target_code.csv', index_label='code')

msg = "対象銘柄入れ替え完了"
# send_message(msg)
print(msg)        
# return {
#     'statusCode': 200,
#     'body': json.dumps('Hello from Lambda!'),
#     }
