import ccxt
from datetime import datetime, timedelta
import fxcmpy
import yfinance as yf
import pandas as pd
import numpy as np
from config.config import *
#import plotly.graph_objects as go

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
    df_final['Adj Close'] = df_final['Close']
    df_final = df_final[['Open', 'High', 'Low', 'Close','Adj Close', 'Volume']]
    df_final.index.name = 'Date'
    df_final = df_final.dropna()
    return df_final

def collect_stock(tickers, start_date='2020-01-01', end_date='2020-11-08'):
    df = yf.download(tickers, start=start_date, end=end_date, progress=False)
    df = df.dropna()
    return df

def collect_fx(connection, ccy_pair='USD/JPY', start_date='2000-01-01', end_date='2020-10-18'):
    """
    Following this website https://fxcmpy.tpq.io/00_quick_start.html#

    :param ccy_pair: currency pair
    :param start_date:
    :param end_date:
    :return: DataFrame
    """
    df = connection.get_candles(ccy_pair, period='D1', start=start_date, end=end_date)
    df['Open'] = (df.bidopen + df.askopen) / 2
    df['High'] = (df.bidhigh + df.askhigh) / 2
    df['Low'] = (df.bidlow + df.asklow) / 2
    df['Close'] = (df.bidclose + df.askclose) / 2
    df['Adj Close'] = df['Close']
    df['Volume'] = df.tickqty
    new_df = df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].copy()

    new_df.index.name = 'Date'
    new_df = new_df.dropna()
    return new_df

if __name__ == '__main__':
    start_date = COLLECT_START_DATE
    end_date = COLLECT_END_DATE

    # Collect FX
    token = 'f561988f2a6a49b2523a6a3094dacb8920879fa9'
    connection = fxcmpy.fxcmpy(access_token=token, log_level='error')

    for symbol in FX_SYMBOLS:
        df_fx = collect_fx(connection, ccy_pair=symbol, start_date=start_date, end_date=end_date)
        df_fx.to_csv("./data/fx_" + symbol.replace("/", "-") + "_" + start_date + "_" + end_date + ".csv")
    connection.close()

    # collect crypto
    for symbol in CRYPTO_SYMBOLS:
        df_crypto = collect_crypto(ccxt.binance(), trading_pair=symbol, start_date=start_date, end_date=end_date)
        df_crypto.to_csv("./data/crypto_" + symbol.replace("/", "-") + "_" + start_date + "_" + end_date + ".csv")

    # Collect stocks
    for symbol in STOCK_SYMBOLS:
        df_stock = collect_stock(symbol, start_date, end_date)
        df_stock.to_csv("./data/stock_" + symbol + "_" + start_date + "_" + end_date + ".csv")