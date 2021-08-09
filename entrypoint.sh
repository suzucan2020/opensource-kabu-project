#!/bin/sh -l


ls

cd work

echo "" > ../github-action.log

echo "write date"
date >> ../github-action.log

echo "scraping stage"
python3 scraping/yahoo-finace-api2.py >> ../github-action.log

echo "sell check stage"
python3 filter/MACD-sell.py >> ../github-action.log

echo "profti stage"
python3 filter/profit.py >> ../github-action.log

echo "chaart stage"
python3 chart/BB.py > ../docs/chart/BB.html
python3 chart/MACD.py > ../docs/chart/MACD.html
python3 chart/IchimokuCloud.py > ../docs/chart/IchimokuCloud.html

echo "Hello $1"
time=$(date)
echo "::set-output name=time::$time"
