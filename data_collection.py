import ccxt
from datetime import datetime, timedelta
import fxcmpy
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go


def collect_crypto(id, time_frame='1d', trading_pair='LTC/BTC', start_date='2010-01-01', end_date='2020-11-17'):
    """
    Fetch OHLCV for cryptocurrencies

    :param id: ccxt.binance() or fetch from https://github.com/ccxt/ccxt/wiki/Exchange-Markets
    :param time_frame: one of following ['m', 'h', 'd']
    :param trading_pair:
    :param start_date: the start date
    :return: dataframe with OHLCV
    """

    first_date = start_date
    num_days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days
    weight = 1
    if num_days > 500:
        weight = int(np.ceil(num_days/500))

    li_df = []
    for _ in range(0, weight):
        start_split = [int(i) for i in start_date.split('-')]
        dt_start = datetime(start_split[0], start_split[1], start_split[2])
        milliseconds_start = int(round(dt_start.timestamp() * 1000))
        candles = id.fetchOHLCV(trading_pair, time_frame, milliseconds_start, 500)
        if len(candles) <= 0:
            break
        df = pd.DataFrame(candles, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df.index = [datetime.fromtimestamp(date).strftime('%Y-%m-%d') for date in df['date'] / 1000]
        df.drop(columns=['date'], inplace=True)
        li_df.append(df)
        start_date = (datetime.strptime(df.iloc[-1].name, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

    df_final = pd.concat(li_df)
    df_final.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    return df_final


def collect_stock(tickers, start_date='2020-01-01', end_date='2020-11-08'):
    df = yf.download(tickers, start=start_date, end=end_date, progress=False)
    return df


def collect_fx(connection, ccy_pair='USD/JPY', start_date='2000-01-01', end_date='2020-10-18'):
    """
    Following this website https://fxcmpy.tpq.io/00_quick_start.html#

    :param ccy_pair: currency pair
    :param start_date:
    :param end_date:
    :return: DataFrame
    """
    # token = 'd0db1914c54a3c30c73256651cdb4ba76de20324'
    # connection = fxcmpy.fxcmpy(access_token=token, log_level='error')
    df = connection.get_candles(ccy_pair, period='D1', start=start_date, end=end_date)
    df['Open'] = (df.bidopen + df.askopen) / 2
    df['High'] = (df.bidhigh + df.askhigh) / 2
    df['Low'] = (df.bidlow + df.asklow) / 2
    df['Close'] = (df.bidclose + df.askclose) / 2
    df['Volume'] = df.tickqty
    new_df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    return new_df


def plot_candlesticks(dates, open_data, high_data, low_data, close_data):
    fig = go.Figure(data=[go.Candlestick(x=dates,
                                         open=open_data, high=high_data,
                                         low=low_data, close=close_data)])
    fig.show()


if __name__ == '__main__':
    start_date = '2000-01-01'
    end_date = '2020-11-18'
    # Collect crypto
    id = ccxt.binance()
    df_crypto = collect_crypto(id, start_date=start_date, end_date=end_date)

    # Collect stocks
    df_stock = collect_stock('AAPL', start_date, end_date)

    # # Collect FX
    df_fx = collect_fx(start_date=start_date, end_date=end_date)
    print("="*100 + "DONE" + "="*100)