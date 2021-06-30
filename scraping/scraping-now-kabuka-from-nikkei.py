import json
import pandas as pd

import urllib.request
import datetime
import time

import boto3
import botocore
from botocore.exceptions import ClientError

def read_df_target_code_from_s3():
    BUCKET_NAME = "kabu-data"
    KEY = "target_code.csv"
    try:
        df = pd.read_csv('s3://'+BUCKET_NAME+'/'+KEY, index_col=0)
    except PermissionError:
        df = pd.DataFrame()
    return df

def is_num(s):
    return s.replace(',', '').replace('.', '').replace('-', '').isnumeric()

def lambda_handler(event, context):
    # TODO implement

    start_time = time.time()
    BUCKET_NAME = "kabu-data"
    KEY = "now_kabuka.csv"
    LOCAL_FILE = "/tmp/" + KEY
    start_time = time.time()
    
    df_target_code = read_df_target_code_from_s3()
    # print(df_target_code)
    codes = df_target_code.index.values.tolist()
    # print(codes)
    
    index = int(event["counter"])
    if index == 0:
        add_file_mode = False
    else:
        add_file_mode = True
    code_list = []
    price_list = []
    open_list = []
    high_list = []
    low_list = []
    volume_list = []
    
    for num in range(index,len(codes)):
        code = codes[num]
        code = str(code)
        print(num,code, ": ",  end="")

        url_name = 'https://www.nikkei.com/nkd/company/?scode=' + code
    
        retry_count = 0
        while True:
            html_data = urllib.request.urlopen(url_name)
            if html_data.getcode() == 200 or retry_count >= 5:
                break
            retry_count += 1
            sleep(1)
    
        counter = 0
        for line in html_data.readlines():
            # print(line)
            decode_line = line.decode('utf-8')
            # print(decode_line)
            if "m-stockPriceElm_value now" in decode_line:
                tmp = decode_line.split(">")[1]
                tmp2 = tmp.split("<")[0]
                tmp3 = tmp2.replace(',', '')
                print(", ", tmp3, end="")
    
                if is_num(tmp3) == True:
                    tmp3 = float(tmp3)
                else:
                    tmp3 = 0.0
                price_list.append(tmp3)
                
            if "m-stockInfo_detail_value" in decode_line:
                # print(decode_line)
                tmp = decode_line.split(">")[1]
                tmp2 = tmp.split("<")[0]
                tmp3 = tmp2.replace(',', '')
                print(", ", tmp3, end="")
    
                if is_num(tmp3) == True:
                    # price_list.append(float(tmp3))
                    tmp3 = float(tmp3)
                else:
                    # price_list.append(0.0)
                    tmp3 = 0.0
    
                # code_list.append(str(code))
                # break
                counter += 1
                if counter == 1:
                    code_list.append(str(code))
                    open_list.append(tmp3)
                elif counter == 2:
                    high_list.append(tmp3)
                elif counter == 3:
                    low_list.append(tmp3)
                else:
                    volume_list.append(tmp3)
                    break
        print("")
        index = num
        time.sleep(0)
        spend_time = time.time() - start_time
        print(spend_time)
        if spend_time > 600:
            break
    
    if add_file_mode == False:
        #df = pd.DataFrame(
        #    data={'price': price_list},
        #    index=code_list,
        #    columns=['price']
        #)
        df = pd.DataFrame(
        data={'Open': open_list, 'High': high_list, 'Low': low_list, 'price': price_list, 'Volume': volume_list},
        index=code_list,
        columns=['Open', 'High', 'Low', 'price', 'Volume']
        )
        print("----  write dataframe  ----")
        print(df)
        # print(df.loc["1352"])
        df.to_csv('s3://'+BUCKET_NAME+'/'+KEY, index_label='code')
        print("------------------------")
    else:
        print("---- read dataframe ----")
        df = pd.read_csv('s3://'+BUCKET_NAME+'/'+KEY, index_col=0)
        print(df)
        print("------------------------")
        print("----  append dataframe  ----")
        # df2 = pd.DataFrame(
        #   data={'price': price_list},
        #   index=code_list,
        #   columns=['price']
        #)
        df2 = pd.DataFrame(
        data={'Open': open_list, 'High': high_list, 'Low': low_list, 'price': price_list, 'Volume': volume_list},
        index=code_list,
        columns=['Open', 'High', 'Low', 'price', 'Volume']
        )
        df = df.append(df2)
        # print(df)
        print("------------------------")
        print("----  write dataframe  ----")
        print(df)
        # print(df.loc["1352"])
        df.to_csv('s3://'+BUCKET_NAME+'/'+KEY, index_label='code')
        print("------------------------")

    # print(index)
    if len(codes) -1 == index:
        result = False
    else:
        result = True
            
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'counter': index + 1,
        'code': code,
        'continue': result
        }
