import pandas as pd
import numpy as np
import talib

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# print(sys.path)
import okap


# input_fname  = "stock-code-list/8man-12man-volume-over40k.txt"
input_fname  = "stock-code-list/all.txt"
output_fname = "stock-code-list/filterIchimoku.txt"
 
year  = 2021
years = [2021,2020]
# codes = [2151]
# codes = okap.read_stock_code_list(input_fname)
df_codes =  pd.read_csv("stock-code-list/all.txt")
            #pd.read_csv("stock-code-list/buy-list.txt")
codes = df_codes["code"]

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
    if len(df) <= 0:
        continue
    
    # print(pd.to_datetime(df['Close']))
    df_new = pd.DataFrame(data=df.Close.values, index=pd.to_datetime(df['Date']), columns=["Close"])
    # print(df_new)
    # print(df_new.resample('M').max())
    # print(df_new.resample('M').max().diff())
    # print(df_new.resample('M').max().pct_change())
    tmp_list = df_new.resample('M').max().pct_change().dropna()
    t = 0
    count = 0
    for x in tmp_list['Close'].values:
        if x >= 0.025:
            count+=1
        t += x
    #    print(x)

    if len(tmp_list) != 0:
        tmp_text = "code: {:5}, total: {:6.3f}, count: {:2}, len: {:2}, tot/l: {:6.3f}, cnt/l: {:.3f}".format(code, t, count, len(tmp_list), t/len(tmp_list), count/len(tmp_list))
        print(tmp_text)
        if count/len(tmp_list) >= 0.6:
            code_list.append(tmp_text)
        # print(df_new)

print("==== up stock ====")
for x in code_list:
    print(x)
    
##     # 終値を一日シフトさせる 
##     okap.make_x_day_shift(df_new,"Close", 1, "Close_1day_ago")
## 
##     row = df_new[-1:]
## ##
##     # 移動平均が終値より高い＆高値が移動平均を超えている＆終値が始値より高い
##     if (row["senkou_b"].values > row["senkou_a"].values) & (row["senkou_b"].values > row["Close_1day_ago"].values) & (row["senkou_b"].values < row["Close"].values):
##         tmp_text = "{},{}".format(row["Date"].values[0], code)
##         print(tmp_text)
##         code_list.append(tmp_text)
##         tmp_title = title[:20]
##         print("HIT: ------------------------> ", tmp_title)
## ##        # print(df_new)
## ##        if len(hit_message + tmp_title + "\n") > 1000:
## ##            message_list.append(hit_message)
## ##            hit_message = "\n" + tmp_title + "\n"
## ##        else:
## ##            hit_message = hit_message + tmp_title + "\n"
## ##
## ##    print("END:  ", code)
## ##    #for index, row in df_new.iterrows():
## ##    #    if(row['2day_positive'] == true and row["2day_colse_goes_up"] == true and row['1day_sma_goes_up'] == true):
## ##    #        print(index)
## with open(output_fname, 'wt') as f:
##     f.write("Date,code"+'\n')
##     for code in code_list:
##         f.write(str(code)+'\n')

##print("以下おすすめの株です")
##if len(hit_message + "\n===========================\n") > 1000:
##    message_list.append(hit_message)
##    message_list.append("\n===========================\n")
##else:
##    hit_message = hit_message + "\n===========================\n"
##    message_list.append(hit_message)
##    
##for message in message_list:
##    print(message)
##    # send_message(message)

# return {
#     'statusCode': 200,
#     'body': json.dumps('Hello from Lambda!')
# }
