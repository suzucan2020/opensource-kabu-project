#!/bin/sh -l

ls
cd work
python3 scraping/yahoo-finace-api2.py

echo "Hello $1"
time=$(date)
echo "::set-output name=time::$time"
