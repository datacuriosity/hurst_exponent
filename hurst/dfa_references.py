import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as ss
import fathon
from fathon import fathonUtils as fu

# This code mainly from dokato (https://github.com/dokato/dfa)
from data_collection import collect_stock


def calc_rms(x, scale):

    """
    Window root mean squared (RMS) with linear detrending

    :param x: numpy array - one dimensional data vector
    :param scale: int - length of window in which RMS will be calculated
    :return: RMS data in each window with length len(x)//scale
    """

    # making an array with data divided in windows
    shape = (x.shape[0] // scale, scale)
    X = np.lib.stride_tricks.as_strided(x, shape=shape)
    # vector of x-axis points to regression
    scale_ax = np.arange(scale)
    rms = np.zeros(X.shape[0])
    for e, xcut in enumerate(X):
        coeff = np.polyfit(scale_ax, xcut, 1)
        xfit = np.polyval(coeff, scale_ax)
        # detrending and computing RMS of each window
        rms[e] = np.sqrt(np.mean((xcut - xfit) ** 2))
    return rms


def dfa(x, scale_lim=[5, 9], scale_dens=0.25, show=False):
    """
    Detrended Flutuation Analysis - measure power law scaling coefficient of the given signal x


    :param x: numpy array - one dimensional vector
    :param scale_lim: list of lengh 2 - boundaries of the scale, where scale means windows among which RMS is calculated.
    [5, 9] --> [2**5, 2**9]
    :param scale_dens: float - density of scale divisions. 0.25 --> we get 2**[5, 5.25, 5.5, ...]
    :param show: boolean - if True, it shows matplotlib log-log plot
    :return:
    - scales: numpy array - vector of scales (x axis)
    - fluct: numpy array - flutuation function values (y axis)
    - alpha: float - estimation of DFA exponent
    """

    # cumulative sum of data with substracted offset
    y = np.cumsum(x - np.mean(x))
    scales = (2 ** np.arange(scale_lim[0], scale_lim[1], scale_dens)).astype(np.int)
    fluct = np.zeros(len(scales))
    # computing RMS for each window
    for e, sc in enumerate(scales):
        fluct[e] = np.sqrt(np.mean(calc_rms(y, sc) ** 2))
    # fitting a line to rms data
    coeff = np.polyfit(np.log2(scales), np.log2(fluct), 1)
    if show:
        fluctfit = 2 ** np.polyval(coeff, np.log2(scales))
        plt.loglog(scales, fluct, 'bo')
        plt.loglog(scales, fluctfit, 'r', label=r'$\alpha$ = %0.2f' % coeff[0])
        plt.title('DFA')
        plt.xlabel(r'$\log_{10}$(time window)')
        plt.ylabel(r'$\log_{10}$<F(t)>')
        plt.legend()
        plt.show()
    # return scales, fluct, coeff[0]
    return coeff[0]


if __name__ == '__main__':

    start_date = '2018-01-01'
    end_date = '2019-12-01'

    stock1 = collect_stock('AAPL', start_date, end_date)
    stock2 = collect_stock('CRM', start_date, end_date)
    stock2['ratio'] = stock2['Close'] / stock1['Close']

    lags = range(2, 20)
    gbm = np.log(np.cumsum(np.random.randn(100000)) + 1000)         # geometric brownian motion
    mr = np.log(np.random.randn(100000) + 1000)                            # mean-reverting
    tr = np.log(np.cumsum(np.random.randn(100000) + 1) + 1000)             # treding series



    print(f'Hurst GBM: {dfa(gbm, show=True)}')
    print(f'Hurst mean-reverting: {dfa(mr, show=True)}')
    print(f'Hurst trending: {dfa(tr, show=True)}')
    print(f'Hurst AAPL {dfa(stock1.Close.to_numpy(), show=True)}')


    # n = 1000
    # x = np.random.randn(n)
    # # computing DFA of signal envelope
    # x = np.abs(ss.hilbert(x))
    # scales, fluct, alpha = dfa(x, show=1)
    # print(scales)
    # print(fluct)
    # print("DFA exponent: {}".format(alpha))