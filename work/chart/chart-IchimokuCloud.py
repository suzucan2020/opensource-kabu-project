import pandas as pd
import numpy as np
import talib

from highcharts import Highstock
# from IPython.display import HTML

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# print(sys.path)
import okap

input_fname  = "stock-code-list/filterMACD.txt"

#years = [2021]
year = 2021
# codes = [1301]
codes = okap.read_stock_code_list(input_fname)


def min_max(in_real):
    min_val = in_real[0]
    max_val = in_real[0]
    # print(in_real[0])
    for price in in_real:
        if min_val > price:
            min_val = price
        if max_val < price:
            max_val = price
    return min_val, max_val

def ichimoku_cloud(in_real):
    length = len(in_real)
    tenkan = [0] * min(9, length)
    kijun = [0] * min(26, length)
    senkou_a = [0] * min(26, length)
    senkou_b = [0] * min(52, length)
    chikou = [0] * min(26, length)

    # print(in_real)
    # print(length)
    # print(tenkan)
    # print(kijun)
    # print(senkou_a)
    # print(senkou_b)
    # print(chikou)

    for i in range(len(in_real)):
        if i >= 9:
            # print(in_real[i-9:i])
            min_val, max_val = min_max(in_real[i-9:i])
            tenkan.append((min_val + max_val) / 2)
        if i >= 26:
            # print(in_real[i-26:i])
            min_val, max_val = min_max(in_real[i-26:i])
            kijun.append((min_val + max_val)/2)
            senkou_a.append((tenkan[i] + kijun[i])/2)
            chikou.append(in_real[i-26])
        if i >= 52:
            # print(in_real[i-52:i])
            min_val, max_val = min_max(in_real[i-52:i])
            senkou_b.append((min_val + max_val)/2)

    # print(in_real)
    # print(length)
    # print(tenkan)
    # print(kijun)
    # print(senkou_a)
    # print(senkou_b)
    # print(chikou)

    senkou_a = ([0] * 26)  + senkou_a[:-26]
    senkou_b = ([0] * 26)  + senkou_b[:-26]
    return tenkan, kijun, senkou_a, senkou_b, chikou

for code in codes:

    # title = okap.read_title_form_s3(str(code), str(year))
    title = str(code)
    # print(title)
    df = okap.read_df_from_s3(str(code), str(year))
    # if not os.path.isfile(file_name):
    #    print("file not exist: ", file_name)
    #    continue
    
    # データの並びをリバースする
    # df = df.reindex(index=df.index[::-1])
    # df.reset_index(inplace=True, drop=True)

    # Ichimoku Cloudを求める
    if len(df.index) >= 9:
        print("call ichimoku_cloud")
        tenkan, kijun, senkou_a, senkou_b, chikou = ichimoku_cloud(df.Close.tolist())
        df['tenkan'] = tenkan
        df['kijun'] = kijun
        df['senkou_a'] = senkou_a
        df['senkou_b'] = senkou_b
        df['chikou'] = chikou
    else:
        df['tenkan'] = 0
        df['kijun'] = 0
        df['senkou_a'] = 0
        df['senkou_b'] = 0
        df['chikou'] = 0

    # print(df)

    H = Highstock()
    
    r = lambda x: round(x, 2)
    # からのデータフレームを作成
    df_html = df
    # 日付を文字列 year/month/day からdatetime(unix時間)に変換
    df_html["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    df_html["Date"] = pd.to_datetime(df["Date"].astype(str), format="%Y-%m-%d")
    # print(df_html)
    # グラフの表示に必要なものだけ選ぶ
    df_html = df_html[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'senkou_a', 'senkou_b', 'chikou']]
    # print(df_html)
    
    groupingUnits = [
        ['week', [1]], 
        ['month', [1, 2, 3, 4, 6]]
    ]
    
    ohlc = [[x[1], r(x[2]), r(x[3]), r(x[4]), r(x[5])] for x in df_html.itertuples()]
    volume = [[x[1], r(x[6])] for x in df_html.itertuples()]
    senkou_a = [[x[1], r(x[7])] for x in df_html.itertuples()]
    senkou_b = [[x[1], r(x[8])] for x in df_html.itertuples()]
    chikou = [[x[1], r(x[9])] for x in df_html.itertuples()]
    
    options = {
        'chart':{
            'renderTo':'container'+str(code),
            'width':400,
            'height':500
        },
        'rangeSelector': {
            'selected': 5
        },
        'title': {
            'text': title
        },
        'yAxis': [
        {
            'labels': {
                'align': 'right',
                'x': -3
            },
            'title': {
                'text': 'OHLC'
            },
            'height': '60%',
            'lineWidth': 2
        },
        {
            'labels': {
                'align': 'right',
                'x': -3
            },
            'title': {
                'text': 'Volume'
            },
            'top': '65%',
            'height': '35%',
            'offset': 0,
            'lineWidth': 2
        }],
    }
    
    H.add_data_set(ohlc, 'candlestick', str(title), dataGrouping={ 'units': groupingUnits })
    H.add_data_set(volume, 'column', 'Volume', yAxis=1, dataGrouping={ 'units': groupingUnits })
    H.add_data_set(senkou_a, 'line', 'senkou_a', dataGrouping={ 'units': groupingUnits })
    H.add_data_set(senkou_b, 'line', 'senkou_b', dataGrouping={ 'units': groupingUnits })
    H.add_data_set(chikou, 'line', 'chikou', dataGrouping={ 'units': groupingUnits })
    H.set_dict_options(options)
    
    html = '''
    {}
    '''.format(H)
    print(html)
    #display(HTML(html))
