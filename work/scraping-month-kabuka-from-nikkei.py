# import json

import urllib.request
import datetime
import time

# import boto3
# import botocore
# from botocore.exceptions import ClientError

import os
import sys

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


def is_num(s):
    return s.replace(',', '').replace('.', '').replace('-', '').isnumeric()

def read_stock_code_list(fname):
    codes = []
    with open(fname, 'r', encoding='utf-8') as fin: # ファイルを開く
        for line in fin.readlines():  # 行を読み込んでfor文で回す
            try:
                code = int(line) # 行を整数（int）に変換する
            except ValueError as e:
                print(e, file=sys.stderr)  # エラーが出たら画面に出力
                continue
            codes.append(code)  # 変換した整数をリストに保存する
    return codes

codes = [1301]
# codes = read_stock_code_list('stock-code-list/all.txt')

start_time = time.time()
 
check_value = []
index = 0 #int(event["counter"])
if index == 0:
    msg = "全銘柄の株価取得開始"
    # send_message(msg)
    print(msg)

# indexからcodes数分ループ
for num in range(index,len(codes)):
    #index = event["counter"]
    #print(index)
    #code = codes[index]
    # 銘柄コードを格納
    code = str(codes[num])
    print(num,":",  code)
    BUCKET_NAME = "kabu-data"
    KEY = code + "_2021.csv"
    # LOCAL_FILE = "/tmp/" + KEY
    LOCAL_FILE = BUCKET_NAME + "/" + KEY


    # print(index)
    dt_now = datetime.datetime.now()
    # dt_now = datetime.datetime(2020, 8, 13)
    dt_now_year = dt_now.strftime('%Y')
    dt_now_month_day = dt_now.strftime('%-m/%-d')
    # print(dt_now_year)
    # print(dt_now_month_day)

    # 株価を持ってくるURL
    url_name = 'https://www.nikkei.com/nkd/company/history/dprice/?scode=' + code

    # URLが開けるまでリトライする
    # サーバーへの負荷を考慮してsleep 1とする
    retry_count = 0
    while True:
        html_data = urllib.request.urlopen(url_name)
        if html_data.getcode() == 200 or retry_count >= 5:
            break
        retry_count += 1
        sleep(1)

    # ファイルの作成、一行目は銘柄コード、2行目はヘッダとする
    with open(LOCAL_FILE, 'w') as fd:
        # print(fd.read())
        fd.write(code)
        fd.write('\nDate,Open,High,Low,Close,Volume,Trading Value')

   # 以下株価抽出処理
    value_list = []
    # value_list.append(dt_now.date())
    hit_date = 0
    counter = 0
    counter2 = 0
    next_read = 0
    # htmlを一行ずつ読み込む
    for line in html_data.readlines():
        # print(line)
        decode_line = line.decode('utf-8')
        # print(decode_line)

        # 月/日のみ取り出す、曜日はいらない
        # 抽出データ例
        # <th class="a-taC">
        #    6/29（火）</th>
        if next_read == 1:
            tmp = decode_line.strip()
            tmp2 = tmp.split('（')
            # print(tmp2[0])
            value_list.append(tmp2[0])
            next_read = 0
            
        # a-taCで引っかけて日付を取り出す
        # ※最初の7回は以下のようにヘッダとなるのですっとばす
        #        <th class="a-taC">日付</th>
        #        <th class="a-taC">始値</th>
        #        <th class="a-taC">高値</th>
        #        <th class="a-taC">安値</th>
        #        <th class="a-taC">終値</th>
        #        <th class="a-taC">売買高</th>
        #        <th class="a-taC">修正後終値</th>
        if "a-taC" in decode_line:
            # print(decode_line)
            counter += 1
            if counter > 7:
                next_read = 1

        # a-taR a-wordBreakAllで引っかけて日付、始値、、、修正後終値を取り出す
        if "a-taR a-wordBreakAll" in decode_line:
            hit_date = 1
        # 数値のみ抜き出す
        if hit_date == 1:
            tmp = decode_line.split(">")[1]
            tmp2 = tmp.split("<")[0]
            # カンマが入ると数値として正しく処理できないで取り除く
            tmp3 = tmp2.replace(',', '')
            if is_num(tmp3) == True:
                value_list.append(float(tmp3))
            else:
                value_list.append(tmp3)
            counter2 += 1

            # counter2 == 6　で一日分のデータとなる
            if counter2 == 6:
                counter2 = 0
                # csvとして扱うため、リストをカンマ区切りで文字列に変換する
                value_str = ','.join(map(str, value_list))
                # print(value_list)
                if counter == 8: # counter == 8 の時最新の日付のデータである
                    check_value = value_str

                # データがない場合value_listは'--'となる
                if '--' in value_list:
                    print(value_list, ": -- bad data")
                # ファイルに追記していく
                else:
                    with open(LOCAL_FILE, 'a') as fd:
                        # print(fd.read())
                        fd.write('\n'+value_str)
                value_list = []
            hit_date = 0

    # s3 = boto3.resource('s3') #S3オブジェクトを取得
    # bucket = s3.Bucket(BUCKET_NAME)
    # bucket.upload_file(LOCAL_FILE, KEY)

    # Lambdaの実行時間は最大15分なので、時間を計測する
    # 処理が完了しない場合、続きから処理させるために必要な情報をreturnする
    time.sleep(0.2)
    spend_time = time.time() - start_time
    print(spend_time)
    index = num   
    # if spend_time > 780:
    #     break

# 最後まで処理が完了した場合lineにメッセージ送信する
if len(codes) -1 == index:
    result = False
    msg = "正常チェック code: " + str(codes[index]) + "\n" + check_value + "\nURL: https://www.nikkei.com/nkd/company/?scode=" + str(codes[index])
    # send_message(msg)
    print(msg)
    msg = "全銘柄の株価取得完了"
    # send_message(msg)
    print(msg)
else:
    result = True

# print(index)
# return {
#     'statusCode': 200,
#     'body': json.dumps('Hello from Lambda!'),
#     'counter': index + 1,
#     'code': code,
#     'continue': result
#     }
