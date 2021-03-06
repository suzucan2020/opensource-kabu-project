# 概要

- scraping
- filter
- chart

## scraping

株価を取得して、csvに保存

- scraping-month-kabuka-from-nikkei.py
  - デフォルト値
    - 対象銘柄：stock-code-list/all.txt 
    - 出力ファイル：kabu-data

```bash
$ pwd
/mnt/work

$ python3 scraping/scraping-month-kabuka-from-nikkei.py
全銘柄の株価取得開始
0 : 1301
0.2258317470550537
1 : 1305
0.5349271297454834
2 : 1306
0.850085973739624
3 : 1308
1.1568846702575684
4 : 1309
1.5134074687957764
5 : 1311
1.8065435886383057
6 : 1312
2.1083755493164062
7 : 1313
['7/7', '--', '--', '--', '--', '--', '--'] : -- bad data
['7/6', '--', '--', '--', '--', '--', '--'] : -- bad data
['7/2', '--', '--', '--', '--', '--', '--'] : -- bad data
['7/1', '--', '--', '--', '--', '--', '--'] : -- bad data
['6/30', '--', '--', '--', '--', '--', '--'] : -- bad data
['6/23', '--', '--', '--', '--', '--', '--'] : -- bad data
['6/18', '--', '--', '--', '--', '--', '--'] : -- bad data
['6/11', '--', '--', '--', '--', '--', '--'] : -- bad data
['6/8', '--', '--', '--', '--', '--', '--'] : -- bad data
2.475443124771118
8 : 1319
['6/24', '--', '--', '--', '--', '--', '--'] : -- bad data
2.799835205078125
9 : 1320
3.1206815242767334
10 : 1321
3.439997911453247
11 : 1322
:
省略
:
正常チェック code: 1301
7/9,2918.0,2918.0,2850.0,2872.0,39000.0,2872.0
URL: https://www.nikkei.com/nkd/company/?scode=1301
全銘柄の株価取得完了
```

## filter

フィルタ条件を満たす銘柄を、ファイルに出力

- 8man-12man-volume-over40k.py
  - すべての銘柄から8万～12万で買える、かつ出来高が40000以上 
  - デフォルト値
    - 対象銘柄：stock-code-list/all.txt 
    - 出力ファイル：stock-code-list/8man-12man-volume-over40k.txt

```bash
$ pwd
/mnt/work

$ python3 scraping/scraping-month-kabuka-from-nikkei.py
対象銘柄入れ替え開始
start:  1301
end:  1301
start:  1305
:
省略
:
start:  9997
9997
end:  9997
       Close        Volume
1356  1183.0    [513006.0]
1360  1073.0  [12345486.0]
1366  1148.0    [418428.6]
1431   871.0     [54140.0]
1571  1041.0    [843223.0]
...      ...           ...
9743   862.0    [193020.0]
9850   960.0     [44260.0]
9900  1021.0    [149240.0]
9979  1053.0     [49280.0]
9997   921.0    [236700.0]

[256 rows x 2 columns]
対象銘柄入れ替え完了
```

- filter0002.py
  - 高値が移動平均線を超えている
  - デフォルト値
    - 対象銘柄：stock-code-list/8man-12man-volume-over40k.txt
    - 出力ファイル：stock-code-list/filter0002.txt

```bash
$ python3 filter/filter0002.py
```

- filterMACD.py
  - MACDがMACDシグナルを超えた（ゴールデンクロス）
  - デフォルト値
    - 対象銘柄：stock-code-list/8man-12man-volume-over40k.txt
    - 出力ファイル：stock-code-list/filterMACD.txt

```bash
$ python3 filter/filterMACD.py
```

## chart

チャートを描画する、github　pagesに書き込む  
github　pages：https://suzucan2020.github.io/opensource-kabu-project/

- chart-BB.py
  - ボリンジャーバンドの描写
  - デフォルト値
    - 対象銘柄：stock-code-list/filter0002.txt
    - period: 20 

```bash
$ python3 chart/chart-BB.py > ../docs/chart/filter0002.html
```

- chart-MACD.py
  - ボリンジャーバンドの描写
  - デフォルト値
    - 対象銘柄：stock-code-list/filterMACD.txt
    - fastperiod: 10
    - slowperiod: 20
    - signalperiod: 5

```
$ python3 chart/chart-MACD.py > ../docs/chart/MACD.html
```
