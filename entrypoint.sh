#!/bin/sh -l

ls
cd work
python3 scraping/yahoo-finace-api2.py
python3 chart/BB.py > ../docs/chart/BB.html
python3 chart/MACD.py > ../docs/chart/MACD.html
python3 chart/IchimokuCloud.py > ../docs/chart/IchimokuCloud.html
git status

echo "Hello $1"
time=$(date)
echo "::set-output name=time::$time"
