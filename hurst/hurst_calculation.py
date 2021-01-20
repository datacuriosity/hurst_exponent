from data_collection import collect_stock
import numpy as np

def hurst(prices, lags):
    tau = []
    lagvec = []

    for lag in lags:
        pp = np.subtract(prices[lag:], prices[:-lag])
        lagvec.append(lag)
        tau.append(np.std(pp))
    m = np.polyfit(np.log(lagvec), np.log(tau), 1)

    return m[0]


if __name__ == '__main__':
    start_date = '2018-01-01'
    end_date = '2019-12-01'

    stock1 = collect_stock('AAPL', start_date, end_date)
    stock2 = collect_stock('CRM', start_date, end_date)
    stock2['ratio'] = stock2['Close'] / stock1['Close']

    lags = range(20, 100)
    np.random.seed(10)
    gbm = np.log(np.cumsum(np.random.randn(100000)) + 1000)         # geometric brownian motion
    mr = np.log(np.random.randn(100000) + 1000)                            # mean-reverting
    tr = np.log(np.cumsum(np.random.randn(100000) + 1) + 1000)             # treding series

    print(f'Hurst GBM: {hurst(gbm, lags)}')
    print(f'Hurst mean-reverting: {hurst(mr, lags)}')
    print(f'Hurst trending: {hurst(tr, lags)}')
    print(f'Hurst AAPL {hurst(list(stock1.Close.to_numpy()), lags)}')


    print("-"*100)


