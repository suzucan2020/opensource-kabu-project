import os
import pandas as pd
import numpy as np

# ---------
# functions
# ---------

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
    file_name = "kabu-data/" + stock_code + "_" + selected_year + ".csv"
    # file_name = stock_code + "_" + selected_year + ".csv"
    title = pd.read_csv(file_name, nrows=1, encoding="shift-jis")
    title = title.columns[0]
    return title

# s3から株価データを取り出し、データをdataframeに落とし込む
def read_df_from_s3(stock_code, selected_year):
    # file_name = "s3://kabu-data/" + stock_code + "_" + selected_year + ".csv"
    file_name = "kabu-data/" + stock_code + "_" + selected_year + ".csv"
    # file_name = stock_code + "_" + selected_year + ".csv"
    # df = pd.read_csv(file_name, header=1, encoding="shift-jis")

    if(os.path.exists(file_name)):
        df = pd.read_csv(file_name, encoding="shift-jis")
        # print(df)
        df.columns = ["Date", "Open", "High", "Low", "Close", "Volume", "Trading Value"]
        df = df.dropna()
        df = df.astype({"Open": float, "High": float, "Low": float, "Close": float, "Volume": float, "Trading Value": float})
        return df
    else:
        cols= ["Date", "Open", "High", "Low", "Close", "Volume", "Trading Value"]
        df = pd.DataFrame(index=[], columns=cols)
        return df

def is_num(s):
    return s.replace(',', '').replace('.', '').replace('-', '').isnumeric()

def read_stock_code_list(fname):
    codes = []
    with open(fname, 'r', encoding='utf-8') as fin: # ファイルを開く
        for line in fin.readlines():  # 行を読み込んでfor文で回す
            try:
                # code = int(line) # 行を整数（int）に変換する
                code = str(line).replace('\n', '')
            except ValueError as e:
                print(e, file=sys.stderr)  # エラーが出たら画面に出力
                continue
            codes.append(code)  # 変換した整数をリストに保存する
    return codes


# シフト関数
# 引数：dataframe、シフトさせるカラム、何日シフトするか、新しいカラム名
def make_x_day_shift(df, shift_column_name, x, new_column_name):
    roll_date = np.roll(df[shift_column_name], x)
    # シフトした部分はinfとする、後々の判定に使用する際にinfとしておけば正しく判定できるため
    roll_date[0:x] = float('inf')
    roll_date[( roll_date == 0)] = float('inf')
    df[new_column_name] = roll_date

# 比較関数
def make_compare_column(df, column_name1, column_name2, new_column_name):
    df[new_column_name] = ( df[column_name1] > df[column_name2] )

# ｘ日上昇が続いているか判定関数
def judge_x_days_goes_up(df, column_name, x, new_column_name):
    tmp_list = []
    for i in range(len(df)):
        if i < x -1:
            tmp_list.append(False)
        else:
            tmp_list.append(np.all( df[i+1-x:i+1][column_name] ))
    df[new_column_name] = tmp_list
