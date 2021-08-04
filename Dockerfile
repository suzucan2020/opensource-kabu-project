# コードを実行するコンテナイメージ
FROM python:3.8

# 必要なコマンドのインストールを行う
RUN apt-get -y update && apt-get install -y wget vim git curl make sudo

# TA-Libのインストールを行う
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    # ARM特有
    wget 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD' -O config.guess && \
    wget 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD' -O config.sub &&\
    ./configure --prefix=/usr && \
    make && \
    make install

RUN pip install ta-lib
RUN pip install pandas
RUN pip install python-highcharts

# アクションのリポジトリからコードファイルをコンテナのファイルシステムパス `/`にコピー
COPY entrypoint.sh /entrypoint.sh

# dockerコンテナが起動する際に実行されるコードファイル (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]
