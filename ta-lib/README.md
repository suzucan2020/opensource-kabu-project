# TA-Lib

## インストール

```
# ta-libのインストール

curl -L http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz -O && tar xzvf ta-lib-0.4.0-src.tar.gz

tar xzvf 'drive/My Drive/Colab Notebooks/ta-lib-0.4.0-src.tar.gz'

cd ta-lib && ./configure --prefix=/usr && make && make install && cd - && pip install ta-lib
```

pythonで`import talib`できればOK！
