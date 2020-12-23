from data_collection import collect_stock
import numpy as np


def hurst(prices, lags):

    # Calculate the array of the variances of the lagged differences
    tau = [np.sqrt(np.std(np.subtract(prices[lag:], prices[:-lag]))) for lag in lags]

    # Use a linear fit to estimate the Hurst Exponent
    poly = np.polyfit(np.log(lags), np.log(tau), 1)

    # Return the Hurst exponent from the polyfit output
    return poly[0]*2.0


if __name__ == '__main__':
    start_date = '2010-01-01'
    end_date = '2020-11-18'
    apple_stock = collect_stock('AAPL', start_date, end_date)

    lags = range(2, 20)
    gbm = np.log(np.cumsum(np.random.randn(100000)) + 1000)         # geometric brownian motion
    mr = np.log(np.random.randn(100000) + 1000)                            # mean-reverting
    tr = np.log(np.cumsum(np.random.randn(100000) + 1) + 1000)             # treding series

    print(f'Hurst GBM: {hurst(gbm, lags)}')
    print(f'Hurst mean-reverting: {hurst(mr, lags)}')
    print(f'Hurst trending: {hurst(tr, lags)}')
    print(f'Hurst AAPL {hurst(list(apple_stock.Close.to_numpy()), lags)}')

