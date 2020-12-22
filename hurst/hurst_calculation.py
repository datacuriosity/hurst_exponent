from data_collection import collect_stock
from numpy import polyfit, subtract, var, log10


def hurst_ernie_chan(p, lags):
    variancetau = []
    tau = []

    for lag in lags:
        #  Write the different lags into a vector to compute a set of tau or lags
        tau.append(lag)

        # Compute the log returns on all days, then compute the variance on the difference in log returns
        # call this pp or the price difference
        pp = subtract(p[lag:], p[:-lag])
        variancetau.append(var(pp))

    # we now have a set of tau or lags and a corresponding set of variances.
    # print tau
    # print variancetau

    # plot the log of those variance against the log of tau and get the slope
    m = polyfit(log10(tau), log10(variancetau), 1)

    hurst = m[0] / 2

    return hurst


if __name__ == '__main__':
    start_date = '2000-01-01'
    end_date = '2020-11-18'
    apple_stock = collect_stock('AAPL', start_date, end_date)
    lags = range(2, 20)

    hurst_final = hurst_ernie_chan(list(apple_stock.Close.to_numpy()), lags)
