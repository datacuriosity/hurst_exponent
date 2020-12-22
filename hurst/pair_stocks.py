from data_collection import collect_stock, collect_fx, collect_crypto
from statsmodels.tsa.stattools import coint
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import fxcmpy
import ccxt


def find_cointegrated_pairs(data):
    n = data.shape[1]
    score_matrix = np.zeros((n, n))
    p_value_matrix = np.ones((n, n))
    keys = data.keys()
    pairs = []

    for i in range(n):
        for j in range(i+1, n):
            s1 = data[keys[i]]
            s2 = data[keys[j]]
            result = coint(s1, s2)
            score_matrix[i, j] = result[0]
            p_value_matrix[i, j] = result[1]
            if result[1] < 0.01:
                pairs.append((keys[i], keys[j]))
    return score_matrix, p_value_matrix, pairs


if __name__ == '__main__':
    start_date = '2017-12-01'
    end_date = '2020-11-18'

    # STOCK
    tech_stocks = ['MSTR', 'AMZN', 'GOOGL', 'AAPL', 'CSCO', 'LRCX', 'NTAP', 'IBM', 'NVDA',
                   'MSFT', 'CRM', 'ORCL', 'SAP', 'SWKS', 'SYNA', 'TSM', 'VIAV']
    tech_stocks = collect_stock(tech_stocks, start_date='2010-01-01', end_date='2020-12-21')['Close']
    scores, p_values, pairs = find_cointegrated_pairs(tech_stocks)
    sns.heatmap(p_values, xticklabels=tech_stocks.columns, yticklabels=tech_stocks.columns, cmap='plasma', mask=(p_values >= 0.01))
    plt.show()

    # FOREX
    token = 'd0db1914c54a3c30c73256651cdb4ba76de20324'
    connection = fxcmpy.fxcmpy(access_token=token, log_level='error')
    instruments = connection.get_instruments()
    ccy_pairs = [ccy for ccy in instruments if '/' in ccy]
    fxs = []
    for ccy in ccy_pairs:
        fx = collect_fx(connection, ccy, start_date='2020-01-01', end_date='2020-12-21').Close.rename(ccy)
        fxs.append(fx)

    all_fx = pd.concat(fxs, axis=1).iloc[:, :-9].dropna()

    scores, p_values, pairs = find_cointegrated_pairs(all_fx)
    sns.heatmap(p_values, xticklabels=all_fx.columns, yticklabels=all_fx.columns, cmap='plasma', mask=(p_values >= 0.01))
    plt.show()

    # CRYPTO
    cryptos = ['ETH/BTC', 'XRP/BTC', 'LTC/BTC', 'BNB/BTC', 'LINK/BTC', 'ADA/BTC', 'EOS/BTC']
    id = ccxt.binance()
    all_cryptos = []
    for crypto in cryptos:
        df_crypto = collect_crypto(id, trading_pair=crypto, start_date=start_date, end_date=end_date).Close.rename(crypto)
        all_cryptos.append(df_crypto)
    all_df = pd.concat(all_cryptos, axis=1)
    scores, p_values, pairs = find_cointegrated_pairs(all_df)
    sns.heatmap(p_values, xticklabels=all_df.columns, yticklabels=all_df.columns, cmap='plasma', mask=(p_values >= 0.01))
    plt.show()





