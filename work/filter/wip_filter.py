from chalice import Chalice
import pandas as pd
import numpy as np
import talib
import json

from datetime import date, datetime
import omitempty

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import desc
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

import random


app = Chalice(app_name='kabu-backend')

Base = declarative_base()

def support_datetime_default(o):
    if isinstance(o, (datetime, date)):
        return  o.isoformat()
    raise TypeError("Type %s is not JSON serializable" % type(o))

class SignalEvent(Base):
    __tablename__ = 'signal_event'

    time = Column(DateTime, primary_key=True, nullable=False)
    product_code = Column(String)
    side = Column(String)
    price = Column(Float)
    units = Column(Integer)

    # def save(self):
    #     db.session.add(self)
    #     db.session.commit()

    @property
    def value(self):
        str_time = self.time.isoformat()
        dict_values = omitempty({
            'time': str_time,
            'product_code': self.product_code,
            'side': self.side,
            'price': self.price,
            'units': self.units,
        })
        if not dict_values:
            return None
        return dict_values
        #return json.dumps(dict_values, default=support_datetime_default)


class SignalEvents(object):
    def __init__(self, signals=None):
        if signals is None:
            self.signals = []
        else:
            self.signals = signals

    def can_buy(self, time):
        if len(self.signals) == 0:
            return True

        last_signal = self.signals[-1]
        if last_signal.side == 'SELL' and last_signal.time < time:
            return True

        return False

    def can_sell(self, time):
        if len(self.signals) == 0:
            return False

        last_signal = self.signals[-1]
        if last_signal.side == 'BUY' and last_signal.time < time:
            return True

        return False

    def buy(self, product_code, time, price, units, save):
        if not self.can_buy(time):
            return False

        signal_event = SignalEvent(time=time, product_code=product_code, side='BUY', price=price, units=units)

        # if save:
        #     signal_event.save()

        self.signals.append(signal_event)
        return True

    def sell(self, product_code, time, price, units, save):
        if not self.can_sell(time):
            return False

        signal_event = SignalEvent(time=time, product_code=product_code, side='SELL', price=price, units=units)

        # if save:
        #     signal_event.save()

        self.signals.append(signal_event)
        return True

    @property
    def profit(self):
        total = 0.0
        before_sell = 0.0
        is_holding = False
        for i in range(len(self.signals)):
            signal_event = self.signals[i]
            if i == 0 and signal_event.side == 'SELL':
                continue
            if signal_event.side == 'BUY':
                total -= signal_event.price * signal_event.units
                is_holding = True
            if signal_event.side ==  'SELL':
                total += signal_event.price * signal_event.units
                is_holding = False
                before_sell = total
        if is_holding:
            return before_sell
        return total

    @property
    def value(self):
        signals = [s.value for s in self.signals]
        if not signals:
            signals = None

        return {'signals': signals}


def read_title_form_s3(stock_code, selected_year):
    file_name = "s3://kabu-data-2020-06-28/" + stock_code + "_" + selected_year + ".csv"
    title = pd.read_csv(file_name, nrows=1, encoding="shift-jis")
    title = title.columns[0]

    return title


def read_df_from_s3(stock_code, selected_year):

    file_name = "s3://kabu-data-2020-06-28/" + stock_code + "_" + selected_year + ".csv"
    df = pd.read_csv(file_name, header=1, encoding="shift-jis")
    df.columns = ["Date", "Open", "High", "Low", "Close", "Volume", "Trading Value"]

    return df


@app.route('/')
def index():
    return {'hello': 'world'}


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.


@app.route('/candle', methods=['GET'], cors=True)
def api_make_handler():

    stock_code = app.current_request.query_params.get('stock_code')
    selected_year = app.current_request.query_params.get('year')
    print(stock_code)
    print(selected_year)

    df = read_df_from_s3(stock_code, selected_year)
    title = read_title_form_s3(stock_code, selected_year)

    return {'stock_name': title, 'candle': json.loads(df.to_json(orient='index'))}


@app.route('/sma', methods=['GET'], cors=True)
def api_sma_handler():

    sma_period1 = app.current_request.query_params.get('smaPeriod1')
    sma_period2 = app.current_request.query_params.get('smaPeriod2')
    sma_period3 = app.current_request.query_params.get('smaPeriod3')

    if not sma_period1:
        sma_period1 = 7
    if not sma_period2:
        sma_period2 = 14
    if not sma_period3:
        sma_period3 = 50

    stock_code = app.current_request.query_params.get('stock_code')
    selected_year = app.current_request.query_params.get('year')

    df = read_df_from_s3(stock_code, selected_year)

    df_sma = pd.DataFrame(index=df.index, columns=[])
    if sma_period1 is not None:
        values = talib.SMA(np.asarray(df.Close, dtype='float64'), int(sma_period1))
        values[np.isnan(values)] = 0
        df_sma['sma'] = values

    if sma_period2 is not None:
        values = talib.SMA(np.asarray(df.Close, dtype='float64'), int(sma_period2))
        values[np.isnan(values)] = 0
        df_sma['sma1'] = values

    if sma_period3 is not None:
        values = talib.SMA(np.asarray(df.Close, dtype='float64'), int(sma_period3))
        values[np.isnan(values)] = 0
        df_sma['sma2'] = values

    return {'smas': json.loads(df_sma.to_json(orient='columns'))}


@app.route('/ema', methods=['GET'], cors=True)
def api_ema_handler():

    ema_period1 = app.current_request.query_params.get('emaPeriod1')
    ema_period2 = app.current_request.query_params.get('emaPeriod2')
    ema_period3 = app.current_request.query_params.get('emaPeriod3')

    if not ema_period1:
        ema_period1 = 7
    if not ema_period2:
        ema_period2 = 14
    if not ema_period3:
        ema_period3 = 50

    stock_code = app.current_request.query_params.get('stock_code')
    selected_year = app.current_request.query_params.get('year')

    df = read_df_from_s3(stock_code, selected_year)

    df_ema = pd.DataFrame(index=df.index, columns=[])
    if ema_period1 is not None:
        values = talib.EMA(np.asarray(df.Close, dtype='float64'), int(ema_period1))
        values[np.isnan(values)] = 0
        df_ema['ema'] = values

    if ema_period2 is not None:
        values = talib.EMA(np.asarray(df.Close, dtype='float64'), int(ema_period2))
        values[np.isnan(values)] = 0
        df_ema['ema1'] = values

    if ema_period3 is not None:
        values = talib.EMA(np.asarray(df.Close, dtype='float64'), int(ema_period3))
        values[np.isnan(values)] = 0
        df_ema['ema2'] = values

    return {'emas': json.loads(df_ema.to_json(orient='columns'))}


@app.route('/bbands', methods=['GET'], cors=True)
def api_bbands_handler():

    str_n = app.current_.query_params.get('bbandsN')
    str_k = app.current_.query_params.get('bbandsK')
    if str_n:
        n = int(str_n)
    if str_k:
        k = float(str_k)
    if not str_n or n < 0 or n is None:
        n = 20
    if not str_k or k < 0 or k is None:
        k = 2.0

    stock_code = app.current_request.query_params.get('stock_code')
    selected_year = app.current_request.query_params.get('year')

    df = read_df_from_s3(stock_code, selected_year)

    df_bbands = pd.DataFrame(index=df.index, columns=[])
    up, mid, down = talib.BBANDS(np.asarray(df.Close, dtype='float64'), n, k, k, 0)

    up[np.isnan(up)] = 0
    mid[np.isnan(mid)] = 0
    down[np.isnan(down)] = 0

    df_bbands['up'] = up
    df_bbands['mid'] = mid
    df_bbands['down'] = down

    return {'bbands': json.loads(df_bbands.to_json(orient='columns'))}


def min_max(in_real):
    min_val = in_real[0]
    max_val = in_real[0]
    # print(in_real[0])
    for price in in_real:
        if min_val > price:
            min_val = price
        if max_val < price:
            max_val = price
    return min_val, max_val


def ichimoku_cloud(in_real):
    length = len(in_real)
    tenkan = [0] * min(9, length)
    kijun = [0] * min(26, length)
    senkou_a = [0] * min(26, length)
    senkou_b = [0] * min(52, length)
    chikou = [0] * min(26, length)

    # print(in_real)
    # print(length)
    # print(tenkan)
    # print(kijun)
    # print(senkou_a)
    # print(senkou_b)
    # print(chikou)

    for i in range(len(in_real)):
        if i >= 9:
            # print(in_real[i-9:i])
            min_val, max_val = min_max(in_real[i-9:i])
            tenkan.append((min_val + max_val) / 2)
        if i >= 26:
            # print(in_real[i-26:i])
            min_val, max_val = min_max(in_real[i-26:i])
            kijun.append((min_val + max_val)/2)
            senkou_a.append((tenkan[i] + kijun[i])/2)
            chikou.append(in_real[i-26])
        if i >= 52:
            # print(in_real[i-52:i])
            min_val, max_val = min_max(in_real[i-52:i])
            senkou_b.append((min_val + max_val)/2)

    # print(in_real)
    # print(length)
    # print(tenkan)
    # print(kijun)
    # print(senkou_a)
    # print(senkou_b)
    # print(chikou)

    senkou_a = ([0] * 26)  + senkou_a[:-26]
    senkou_b = ([0] * 26)  + senkou_b[:-26]
    return tenkan, kijun, senkou_a, senkou_b, chikou


@app.route('/ichimoku_cloud', methods=['GET'], cors=True)
def api_ichimoku_cloud_handler():

    stock_code = app.current_request.query_params.get('stock_code')
    selected_year = app.current_request.query_params.get('year')

    df = read_df_from_s3(stock_code, selected_year)

    df_ichimoku_cloud = pd.DataFrame(index=df.index, columns=[])
    if len(df.index) >= 9:
        print("call ichimoku_cloud")
        tenkan, kijun, senkou_a, senkou_b, chikou = ichimoku_cloud(df.Close.tolist())
        df_ichimoku_cloud['tenkan'] = tenkan
        df_ichimoku_cloud['kijun'] = kijun
        df_ichimoku_cloud['senkou_a'] = senkou_a
        df_ichimoku_cloud['senkou_b'] = senkou_b
        df_ichimoku_cloud['chikou'] = chikou
    else:
        df_ichimoku_cloud['tenkan'] = 0
        df_ichimoku_cloud['kijun'] = 0
        df_ichimoku_cloud['senkou_a'] = 0
        df_ichimoku_cloud['senkou_b'] = 0
        df_ichimoku_cloud['chikou'] = 0

    return {'ichimoku_cloud': json.loads(df_ichimoku_cloud.to_json(orient='columns'))}


@app.route('/rsi', methods=['GET'], cors=True)
def api_rsi_handler():

    rsi_period1 = app.current_request.query_params.get('rsiPeriod')
    if not rsi_period1:
        rsi_period1 = 14

    stock_code = app.current_request.query_params.get('stock_code')
    selected_year = app.current_request.query_params.get('year')

    df = read_df_from_s3(stock_code, selected_year)

    df_rsi = pd.DataFrame(index=df.index, columns=[])
    if rsi_period1 is not None:
        values = talib.RSI(np.asarray(df.Close, dtype='float64'), int(rsi_period1))
        values[np.isnan(values)] = 0
        df_rsi['values'] = values

    return {'rsi': json.loads(df_rsi.to_json(orient='columns'))}


@app.route('/macd', methods=['GET'], cors=True)
def api_macd_handler():

    macd_period1 = app.current_request.query_params.get('macdPeriod1')
    macd_period2 = app.current_request.query_params.get('macdPeriod2')
    macd_period3 = app.current_request.query_params.get('macdPeriod3')

    if not macd_period1:
        macd_period1 = 12
    if not macd_period2:
        macd_period2 = 26
    if not macd_period3:
        macd_period3 = 9

    stock_code = app.current_request.query_params.get('stock_code')
    selected_year = app.current_request.query_params.get('year')

    df = read_df_from_s3(stock_code, selected_year)

    df_macd = pd.DataFrame(index=df.index, columns=[])
    if macd_period1 is not None:
        macd, macd_signal, macd_hist = talib.MACD(np.asarray(df.Close, dtype='float64'), int(macd_period1), int(macd_period2), int(macd_period3))
        macd[np.isnan(macd)] = 0
        macd_signal[np.isnan(macd_signal)] = 0
        macd_hist[np.isnan(macd_hist)] = 0
        df_macd['macd'] = macd
        df_macd['macd_signal'] = macd_signal
        df_macd['macd_hist'] = macd_hist

    return {'macd': json.loads(df_macd.to_json(orient='columns'))}


@app.route('/events', methods=['GET'], cors=True)
def api_events_handler():

    stock_code = app.current_request.query_params.get('stock_code')
    selected_year = app.current_request.query_params.get('year')

    df = read_df_from_s3(stock_code, selected_year)
    
    signal_events = SignalEvents()
    
    tommorow_buy = 0
    sell_flag = 0
    today_positive = 0
    yesterday_positive = 0
    yesterday_close = df.at[0, 'Close']
    for index, item in df.iterrows():

        if sell_flag == 1:
            str_date = item['Date']
            dt = datetime.strptime(str_date, '%Y-%m-%d')
            buy_open = item['Open']
            signal_events.sell(stock_code, dt, float(buy_open), 100, False)
            sell_flag = 0
            tommorow_buy = 0

        if tommorow_buy == 1:
            str_date = item['Date']
            dt = datetime.strptime(str_date, '%Y-%m-%d')
            buy_open = item['Open']
            signal_events.buy(stock_code, dt, float(buy_open), 100, False)
            sell_flag = 1


        if item['Close'] >= item['Open']:
            today_positive = 1
        else:
            today_positive = 0

        if today_positive==1 and yesterday_positive == 1 and item['Close'] >= yesterday_close:
            tommorow_buy = 1
            print("item: ", item["Date"])
            print("today_positive: ", today_positive)
            print("yesterday_positive: ", yesterday_positive)

        yesterday_positive = today_positive
        yesterday_close = item['Close']
        
        
    for x in signal_events.value["signals"]:
        print(x)
        
    return {'events': signal_events.value, 'profit': signal_events.profit}
