#!/bin/sh -l

date > ../github-action.log
ls
cd work
echo "scraping stage"
python3 scraping/yahoo-finace-api2.py >> ../github-action.log

echo "chaart stage"
python3 chart/BB.py > ../docs/chart/BB.html
python3 chart/MACD.py > ../docs/chart/MACD.html
python3 chart/IchimokuCloud.py > ../docs/chart/IchimokuCloud.html

echo "Hello $1"
time=$(date)
echo "::set-output name=time::$time"
