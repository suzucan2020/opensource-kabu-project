import pandas as pd
import numpy as np
import talib

from highcharts import Highstock
# from IPython.display import HTML

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

year  = 2021
years = [2021]
codes = [
"9468"
]

for code in codes:

    title = read_title_form_s3(str(code), str(year))
    # print(title)
    df = read_df_from_s3(str(code), str(year))
    # if not os.path.isfile(file_name):
    #    print("file not exist: ", file_name)
    #    continue
    
    # データの並びをリバースする
    df = df.reindex(index=df.index[::-1])
    df.reset_index(inplace=True, drop=True)
 
    # # talib$Onparray$K$9$k.7?$Odouble$K$9$k
    # 5日移動平均を求める
    sma = talib.SMA(np.asarray(df.Close, dtype='float64'), 5)
    # nanデータは0とする
    # sma[np.isnan(sma)] = 0.0
    sma[np.isnan(sma)] = sma[4]
    # print(sma)
    df['sma'] = sma
    
    # BBを求める
    up, mid, down = talib.BBANDS(np.asarray(df.Close, dtype='float64'), 5, 1, 1, 0)
    up[np.isnan(up)] = 0
    mid[np.isnan(mid)] = 0
    down[np.isnan(down)] = 0 
    df['up'] = up
    df['mid'] = mid
    df['down'] = down

    print(df)

    H = Highstock()
    
    r = lambda x: round(x, 2)
    # からのデータフレームを作成
    df_html = df
    # 日付を文字列 year/month/day からdatetime(unix時間)に変換
    df_html["Date"] = pd.to_datetime(df["Date"].astype(str), format="%m/%d")
    print(df_html)
    # グラフの表示に必要なものだけ選ぶ
    df_html = df_html[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'up', 'mid', 'down']]
    # print(df_html)
    
    groupingUnits = [
        ['week', [1]], 
        ['month', [1, 2, 3, 4, 6]]
    ]
    
    ohlc = [[x[1], r(x[2]), r(x[3]), r(x[4]), r(x[5])] for x in df_html.itertuples()]
    volume = [[x[1], r(x[6])] for x in df_html.itertuples()]
    up = [[x[1], r(x[7])] for x in df_html.itertuples()]
    mid = [[x[1], r(x[8])] for x in df_html.itertuples()]
    down = [[x[1], r(x[9])] for x in df_html.itertuples()]
    
    options = {
        'chart':{
            'width':1600,
            'height':900
        },
        'rangeSelector': {
            'selected': 1
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
    
    H.add_data_set(ohlc, 'candlestick', 'bitcoin', dataGrouping={ 'units': groupingUnits })
    H.add_data_set(volume, 'column', 'Volume', yAxis=1, dataGrouping={ 'units': groupingUnits })
    H.add_data_set(up, 'line', 'up', dataGrouping={ 'units': groupingUnits })
    H.add_data_set(mid, 'line', 'mid', dataGrouping={ 'units': groupingUnits })
    H.add_data_set(down, 'line', 'down', dataGrouping={ 'units': groupingUnits })
    H.set_dict_options(options)
    
    html = '''
    {}
    '''.format(H)
    print(html)
    #display(HTML(html))
