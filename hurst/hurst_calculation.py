from data_collection import collect_stock
import numpy as np
from sklearn.linear_model import LinearRegression


def split_chunks(series_data, num_chunks):

    mean_rescaled_ranges = []
    num_observations = []
    for i in range(num_chunks):
        series = np.array_split(series_data, 2**i)
        num_observations.append(np.log(series[0].shape[0]))
        rescaled_ranges = []
        for arr in series:
            mean = arr.mean()
            std = np.std(arr)

            mean_adjusted = arr - mean
            cumulative_deviation = np.cumsum(mean_adjusted)
            range_R = cumulative_deviation.max() - cumulative_deviation.min()

            rescaled_range = range_R / std
            rescaled_ranges.append(rescaled_range)

        mean_rescaled_ranges.append(np.log(np.mean(rescaled_ranges)))

    return np.array(num_observations), np.array(mean_rescaled_ranges)


def hurst_exp(log_num_observations, log_mean_rescaled_ranges):

    linear = LinearRegression()
    linear.fit(log_num_observations.reshape(-1, 1), log_mean_rescaled_ranges)
    return linear.coef_[0]


if __name__ == '__main__':
    start_date = '2000-01-01'
    end_date = '2020-11-18'
    apple_stock = collect_stock('AAPL', start_date, end_date)
    log_num_observations, log_mean_rescaled_ranges = split_chunks(apple_stock.Close.to_numpy(), 3)
    hurst_ex = hurst_exp(log_num_observations, log_mean_rescaled_ranges)
