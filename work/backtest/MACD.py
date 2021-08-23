import pandas as pd
import numpy as np
import talib

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# print(sys.path)
import okap

pd.set_option('display.max_rows', 500)

input_fname  = \
        "stock-code-list/up.txt"
        # "stock-code-list/all.txt"
        # "stock-code-list/buy-list.txt"
        # "stock-code-list/8man-12man-volume-over40k.txt"
        # "stock-code-list/all.txt"

output_fname = "stock-code-list/filterMACD.txt"
 
year  = 2021
years = [2021,2020]
# codes = ['INTC']
codes = okap.read_stock_code_list(input_fname)

code_list = []

tmp_message = "\
===========================\n\
START backtest \n\
MACD0以上で買い、0以下で売り\n\
===========================\
"

message_list = []
all_profit_percent = 0
print(tmp_message) 
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
    
    # 売買判定に使うものをピックアップ
    df_new = pd.DataFrame(index=df.index, columns=[])
    df_new['Date'] = df.Date
    df_new['Close'] = df.Close
    df_new['macd'] = df.macd
    df_new['macd_signal'] = df.macd_signal
    df_new['macd_hist'] = df.macd_hist
 
    # MACDを一日シフトさせる 
    okap.make_x_day_shift(df_new,"macd", 1, "macd_1day_ago")
    # print(df_new)
    # print(df_new[ (df_new['macd'] > 0) & (df_new['macd_1day_ago'] <0) ])
    
    print("====")
    print("code: ", code)
    # print("-")
    total_profit = 0
    total_profit_percent = 0
    buy_price = 0
    buy_flag = 0
    for index, row in df_new.iterrows():
        if row['macd'] > 0  and row['macd_1day_ago'] < 0:
            print('BUY: {} {:6.2f}'.format(row['Date'], row['Close']))
            buy_flag = 1
            buy_price = row['Close']
        if row['macd'] < 0  and row['macd_1day_ago'] > 0 and buy_flag == 1:
            buy_flag = 0
            profit = row['Close'] - buy_price
            profit_percent = profit / buy_price * 100
            total_profit += profit
            total_profit_percent += profit_percent
            print('SEL: {} {:6.2f} profit: {:>6.2f} /buy_price: {:6.2f}%'.format(row['Date'], row['Close'], profit, profit_percent))
        if (len(df_new) -1) == index and buy_flag == 1:
            buy_flag = 0
            profit = row['Close'] - buy_price
            profit_percent = profit / buy_price * 100
            total_profit += profit
            total_profit_percent += profit_percent
            print('SEL: {} {:6.2f} profit: {:>6.2f} /buy_price: {:6.2f}%'.format(row['Date'], row['Close'], profit, profit_percent))
    all_profit_percent += total_profit_percent
    # print("-")
    print('code: {:6}, total_profit: {:>6.2f} total_profit_percent: {:>6.2f}%'.format(code, total_profit, total_profit_percent))
 
print("==== all ====")
print('all_profit_percent: {:>6.2f}%, len(codes): {}, {:>6.2f}%'.format(all_profit_percent, len(codes), all_profit_percent/len(codes)))
