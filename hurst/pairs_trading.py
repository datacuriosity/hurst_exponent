from data_collection import collect_stock, collect_fx, collect_crypto
from statsmodels.tsa.stattools import coint
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


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
    # Technology stocks
    tech_stocks = ['MSTR', 'AMZN', 'GOOGL', 'AAPL', 'CSCO', 'LRCX', 'NTAP', 'IBM', 'NVDA',
                   'MSFT', 'CRM', 'ORCL', 'SAP', 'SWKS', 'SYNA', 'TSM', 'VIAV']
    tech_stocks = collect_stock(tech_stocks, start_date='2010-01-01', end_date='2020-12-21')['Close']

    scores, p_values, pairs = find_cointegrated_pairs(tech_stocks)
    sns.heatmap(p_values, xticklabels=tech_stocks.columns, yticklabels=tech_stocks.columns, cmap='plasma', mask=(p_values >= 0.01))
    plt.show()

    # Forex



