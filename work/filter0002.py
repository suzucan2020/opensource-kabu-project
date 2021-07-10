import pandas as pd
import numpy as np
import talib

import okap

year  = 2021
years = [2021,2020]
# codes = [9468]
codes = okap.read_stock_code_list('stock-code-list/8man-12man-volume-over40k.txt')

code_list = []

# hit_message = "====================\nおすすめの株\n8万以上12万以下\n2日連続で陽線\n5日移動平均線が上昇\n===========================\n"
hit_message = "====================\nおすすめの株\n8万以上12万以下\n終値が移動平均線より低い＆高値が移動平均線を超えている\n===========================\n"
message_list = []
for code in codes:

    title = okap.read_title_form_s3(str(code), str(year))
    # print(title)
    df = okap.read_df_from_s3(str(code), str(year))
    # if not os.path.isfile(file_name):
    #    print("file not exist: ", file_name)
    #    continue
    df = df.reindex(index=df.index[::-1])
    df.reset_index(inplace=True, drop=True)
    # print(df)

    # # talib$Onparray$K$9$k.7?$Odouble$K$9$k
    # 5日移動平均を求める
    sma = talib.SMA(np.asarray(df.Close, dtype='float64'), 20)
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
    okap.make_compare_column(df_new, "Close", "Open", "today_positive")
    # 二日連続で上昇しているかどうか
    okap.judge_x_days_goes_up(df_new, "today_positive", 2, "2day_positive")

    # 終値を一日シフトさせる 
    okap.make_x_day_shift(df_new,"Close", 1, "Close_1day_ago")
    # 今日の終値は昨日の終値より高いかどうか
    okap.make_compare_column(df_new, "Close", "Close_1day_ago", "1day_Colse_goes_up")
    # 2日連続で終値が上昇しているかどうか
    okap.judge_x_days_goes_up(df_new, "1day_Colse_goes_up", 2, "2day_Colse_goes_up")

    df_new['sma'] = df.sma
    # 移動平均を1日シフト
    okap.make_x_day_shift(df_new, "sma", 1, "sma_1day_ago")
    # 移動平均が昨日より高いかどうか
    okap.make_compare_column(df_new, "sma", "sma_1day_ago", "1day_sma_goes_up")


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
        code_list.append(code)
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
with open("stock-code-list/filter0002.txt", 'wt') as f:
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
