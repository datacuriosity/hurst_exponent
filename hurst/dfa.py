import numpy as np
from data_collection import collect_stock


def dfa_coef(prices, len_n=10):
    """

    :param prices:
    :param len_n: number of boxes
    :return:
    """
    num_time = len(prices)
    cumsum_price = np.cumsum(prices - np.mean(prices))
    boxes = list(range(0, num_time, len_n))
    len_boxes = len(boxes)
    y_predicted = np.zeros((len_boxes-1, len_n))
    cumsum_price_post = np.zeros((len_boxes-1, len_n))
    for i in range(len_boxes-1):
        if i >= len_boxes-1:
            sub_price = cumsum_price[boxes[i]: ]
            indices = list(range(boxes[i], len(cumsum_price)))
        else:
            sub_price = cumsum_price[boxes[i]:boxes[i+1]]
            indices = list(range(boxes[i], boxes[i+1]))
        coef = np.polyfit(indices, sub_price, 1)
        y_n = np.polyval(coef, indices)
        y_predicted[i] = y_n
        cumsum_price_post[i] = sub_price

    fn = np.sqrt(np.mean((cumsum_price_post - y_predicted)**2, axis=0))
    final_coef = np.polyfit(np.log2(range(1, len_n+1)), np.log2(fn), 1)

    return final_coef[0]


if __name__ == '__main__':

    start_date = '2018-01-01'
    end_date = '2019-12-01'

    stock1 = collect_stock('AAPL', start_date, end_date)

    gbm = np.log(np.cumsum(np.random.randn(100000)) + 1000)         # geometric brownian motion
    mr = np.log(np.random.randn(100000) + 1000)                            # mean-reverting
    tr = np.log(np.cumsum(np.random.randn(100000) + 1) + 1000)             # treding series
    price = stock1.Close.to_numpy()

    print(f'Hurst GBM: {dfa_coef(gbm)}')
    print(f'Hurst mean-reverting: {dfa_coef(mr)}')
    print(f'Hurst trending: {dfa_coef(tr)}')
    print(f'Hurst AAPL {dfa_coef(stock1.Close.to_numpy())}')
