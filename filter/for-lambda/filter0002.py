import json
import pandas as pd
import numpy as np
import talib


import sys
import urllib.parse
import urllib.request
import os

# LINE notify's API
LINE_TOKEN= os.environ.get("LINE_NOTIFY_API_KEY")
LINE_NOTIFY_URL="https://notify-api.line.me/api/notify"
def send_message(msg):
    method = "POST"
    headers = {"Authorization": "Bearer %s" % LINE_TOKEN}
    payload = {"message": msg}
    try:
        payload = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(
            url=LINE_NOTIFY_URL, data=payload, method=method, headers=headers)
        urllib.request.urlopen(req)
    except Exception as e:
        print ("Exception Error: ", e)
        sys.exit(1)

def read_title_form_s3(stock_code, selected_year):
    file_name = "s3://kabu-data/" + stock_code + "_" + selected_year + ".csv"
    title = pd.read_csv(file_name, nrows=1, encoding="shift-jis")
    title = title.columns[0]

    return title


def read_df_from_s3(stock_code, selected_year):

    file_name = "s3://kabu-data/" + stock_code + "_" + selected_year + ".csv"
    df = pd.read_csv(file_name, header=1, encoding="shift-jis")
    df.columns = ["Date", "Open", "High", "Low", "Close", "Volume", "Trading Value"]
    df = df.dropna()
    df = df.astype({"Open": float, "High": float, "Low": float, "Close": float, "Volume": float, "Trading Value": float})

    return df


def make_x_day_shift(df, shift_column_name, x, new_column_name):
    roll_date = np.roll(df[shift_column_name], x)
    roll_date[0:x] = float('inf')
    roll_date[( roll_date == 0)] = float('inf')
    df[new_column_name] = roll_date


def make_compare_column(df, column_name1, column_name2, new_column_name):
    df[new_column_name] = ( df[column_name1] > df[column_name2] )

def judge_x_days_goes_up(df, column_name, x, new_column_name):
    tmp_list = []
    for i in range(len(df)):
        if i < x -1:
            tmp_list.append(False)
        else:
            tmp_list.append(np.all( df[i+1-x:i+1][column_name] ))
    df[new_column_name] = tmp_list

codes = [
"9991"
]

def lambda_handler(event, context):
    # TODO implement
    
    # hit_message = "====================\nおすすめの株\n8万以上12万以下\n2日連続で陽線\n5日移動平均線が上昇\n===========================\n"
    hit_message = "====================\nおすすめの株\n8万以上12万以下\n終値が移動平均線より低い＆高値が移動平均線を超えている\n===========================\n"
    message_list = []
    for code in codes:

        title = read_title_form_s3(str(code), "2020")
        # print(title)
        df = read_df_from_s3(str(code), "2020")
        # if not os.path.isfile(file_name):
        #    print("file not exist: ", file_name)
        #    continue
       
        # # talib$Onparray$K$9$k.7?$Odouble$K$9$k
        sma = talib.SMA(np.asarray(df.Close, dtype='float64'), 5)
        sma[np.isnan(sma)] = 0.0
        # print(sma)
        df['sma'] = sma
    
        df_new = pd.DataFrame(index=df.index, columns=[])
        df_new["Open"] = df.Open
        df_new["Close"] = df.Close
        df_new["High"] = df.High
        # df_new["diff"] = (df.Close - df.Open)
    
        make_compare_column(df_new, "Close", "Open", "today_positive")
        judge_x_days_goes_up(df_new, "today_positive", 2, "2day_positive")
    
        make_x_day_shift(df_new,"Close", 1, "Close_1day_ago")
        make_compare_column(df_new, "Close", "Close_1day_ago", "1day_Colse_goes_up")
        judge_x_days_goes_up(df_new, "1day_Colse_goes_up", 2, "2day_Colse_goes_up")
    
        df_new['sma'] = df.sma
        make_x_day_shift(df_new, "sma", 1, "sma_1day_ago")
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
        send_message(message)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
