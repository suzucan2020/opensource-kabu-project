import pandas as pd
import numpy as np
import talib

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# print(sys.path)
import okap

pd.set_option('display.max_rows', 500)

# input_fname  = "stock-code-list/8man-12man-volume-over40k.txt"
input_fname  = "stock-code-list/all.txt"
output_fname = "stock-code-list/filterMACD.txt"
 
year  = 2021
years = [2021,2020]
codes = ['MOH']
# codes = okap.read_stock_code_list(input_fname)

code_list = []

# hit_message = "====================\nおすすめの株\n8万以上12万以下\n2日連続で陽線\n5日移動平均線が上昇\n===========================\n"
hit_message = "====================\nおすすめの株\nMACDがMACDシグナルを突き抜けました\n===========================\n"
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
    # print(df[df['macd_hist'] > 0])
    
    df_new = pd.DataFrame(index=df.index, columns=[])
    df_new['Date'] = df.Date
    df_new['Close'] = df.Close
    df_new['macd'] = df.macd
    df_new['macd_signal'] = df.macd_signal
    df_new['macd_hist'] = df.macd_hist
 
    # 終値を一日シフトさせる 
    okap.make_x_day_shift(df_new,"macd", 1, "macd_1day_ago")
    print(df_new)
    # print(df_new[ (df_new['macd'] > 0) & (df_new['macd_1day_ago'] <0) ])

    for index, row in df_new.iterrows():
        if row['macd'] > 0  and row['macd_1day_ago'] < 0:
            print('BUY: ', row['Date'], row['Close'])
        if row['macd'] < 0  and row['macd_1day_ago'] > 0:
            print('SEL: ', row['Date'], row['Close'])


    # 終値を一日シフトさせる 
    okap.make_x_day_shift(df_new,"macd_hist", 1, "macd_hist_1day_ago")

    row = df_new[-1:]

    # 移動平均が終値より高い＆高値が移動平均を超えている＆終値が始値より高い
    if (row["macd_hist"].values > 0) & (row["macd_hist_1day_ago"].values <= 0):
        code_list.append(code)
        tmp_title = title[:20]
        print("HIT: ------------------------> ", tmp_title)
        # print(df_new)
        if len(hit_message + tmp_title + "\n") > 1000:
            message_list.append(hit_message)
            hit_message = "\n" + tmp_title + "\n"
        else:
            hit_message = hit_message + tmp_title + "\n"

    print("END:  ", code)
    #for index, row in df_new.iterrows():
    #    if(row['2day_positive'] == true and row["2day_colse_goes_up"] == true and row['1day_sma_goes_up'] == true):
    #        print(index)
with open(output_fname, 'wt') as f:
    for code in code_list:
        f.write(str(code)+'\n')

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
