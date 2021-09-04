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

print("arg[0]: {}, arg[1]: {}".format(sys.argv[0], sys.argv[1]))
input_fname  =  str(sys.argv[1])
                # "stock-code-list/filterIchimoku.txt"
                # "stock-code-list/MACD-over-0.txt"
                # "stock-code-list/buy-list.txt"
                # "stock-code-list/filter0002.txt" 
                # "stock-code-list/filterMACD.txt"

#years = [2021]
year = 2021
# codes = [1301]
# codes = okap.read_stock_code_list(input_fname)
df_codes =  pd.read_csv(input_fname)
codes = df_codes["code"]

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
        macd, macd_signal, macd_hist = talib.MACD(np.asarray(df.Close, dtype='float64'), int(macd_period1), int(macd_period2), int(macd_period3))
        # macd[np.isnan(macd)] = 0
        # macd_signal[np.isnan(macd_signal)] = 0
        # macd_hist[np.isnan(macd_hist)] = 0
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        df['macd_hist'] = macd_hist

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
    df_html = df_html[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'macd', 'macd_signal', 'macd_hist']]
    # print(df_html)
    
    groupingUnits = [
        ['week', [1]], 
        ['month', [1, 2, 3, 4, 6]]
    ]
    
    ohlc = [[x[1], r(x[2]), r(x[3]), r(x[4]), r(x[5])] for x in df_html.itertuples()]
    volume = [[x[1], r(x[6])] for x in df_html.itertuples()]
    macd = [[x[1], r(x[7])] for x in df_html.itertuples()]
    macd_signal = [[x[1], r(x[8])] for x in df_html.itertuples()]
    macd_hist = [[x[1], r(x[9])] for x in df_html.itertuples()]
    
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
    
    # H.add_data_set(ohlc, 'candlestick', str(title), dataGrouping={ 'units': groupingUnits })
    H.add_data_set(volume, 'column', 'Volume', yAxis=1, dataGrouping={ 'units': groupingUnits })
    H.add_data_set(macd, 'line', 'macd', dataGrouping={ 'units': groupingUnits })
    H.add_data_set(macd_signal, 'line', 'macd_signal', dataGrouping={ 'units': groupingUnits })
    H.add_data_set(macd_hist, 'column', 'macd_hist', dataGrouping={ 'units': groupingUnits })
    H.set_dict_options(options)
    
    html = '''
    {}
    '''.format(H)
    print(html)
    #display(HTML(html))
