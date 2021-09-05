#!/bin/sh -l

ls

cd work

LOG_DIR="../github-action-log/`date '+%Y-%m'`"
LOG_FILE=$LOG_DIR/"`date '+%d'`.log"
echo $LOG_FILE

mkdir -p $LOG_DIR
touch $LOG_FILE

echo "write date"
date > $LOG_FILE

echo "scraping stage"
python3 scraping/yahoo-finace-api2.py stock-code-list/buy-list.txt >> $LOG_FILE

echo "sell check stage"
python3 filter/MACD-sell.py >> $LOG_FILE

echo "profit stage"
python3 filter/profit.py >> $LOG_FILE

echo "chart stage"
python3 chart/BB.py stock-code-list/buy-list.txt > ../docs/chart/BB.html
python3 chart/MACD.py stock-code-list/buy-list.txt > ../docs/chart/MACD.html
python3 chart/IchimokuCloud.py stock-code-list/buy-list.txt > ../docs/chart/IchimokuCloud.html

echo "Hello $1"
time=$(date)
echo "::set-output name=time::$time"
