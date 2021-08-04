# コードを実行するコンテナイメージ
FROM python:3.8

# 必要なコマンドのインストールを行う
RUN apt-get -y update && apt-get install -y wget vim git curl make sudo

# TA-Libのインストールを行う
# RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
#     tar -xzf ta-lib-0.4.0-src.tar.gz && \
#     cd ta-lib/ && \
#     ./configure --prefix=/usr && \
#     make && \
#     make install
# 
# RUN pip install ta-lib
# RUN pip install pandas
# RUN pip install python-highcharts
# RUN pip install yahoo_finance_api2

# # アクションのリポジトリからコードファイルをコンテナのファイルシステムパス `/`にコピー
# COPY entrypoint.sh /entrypoint.sh
# 
# # dockerコンテナが起動する際に実行されるコードファイル (`entrypoint.sh`)
# ENTRYPOINT ["/entrypoint.sh"]

COPY ./work /tmp
WORKDIR /tmp/work

# CMD ["ls -l"]
