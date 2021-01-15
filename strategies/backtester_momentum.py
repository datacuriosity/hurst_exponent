import backtrader as bt
from datetime import datetime
import os
import pandas as pd
from hurst.hurst_calculation import *
from strategies import *
from config.config import *

MOVING_AVERAGE_SLOW = 20
MOVING_AVERAGE_FAST = 10
MOVING_AVERAGE_UPPER_LIMIT_MULTIPLIER = 2

def calculateAverageSharpeRatio(ratios, results, file, hurst_val, hurst_table):
    if len(ratios) > 0:
        avg_sharpe = sum(ratios) / len(ratios)
        print(file + " has average sharpe " + str(avg_sharpe))
        results[file.split('_')[1]] = avg_sharpe
        hurst_table[file.split('_')[1]] = hurst_val
    else:
        print("No suitable sharpe found for " + file)

def runBacktest(pfast, pslow, file, ratios):
    cerebro = bt.Cerebro()

    data = bt.feeds.YahooFinanceCSVData(
        dataname='../data/' + file,
        fromdate=datetime.strptime(TEST_START_DATE, '%Y-%M-%d'),
        todate=datetime.strptime(TEST_END_DATE, '%Y-%M-%d'),
    )

    cerebro.adddata(data)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.addsizer(bt.sizers.AllInSizer)
    start_portfolio_value = cerebro.broker.getvalue()
    cerebro.addstrategy(MAcrossover, pfast=pfast, pslow=pslow)

    run = cerebro.run()
    sharpe = run[0].analyzers.sharpe_ratio.ratio
    if sharpe and sharpe > SHARPE_LOWER_LIMIT and sharpe < SHARPE_UPPER_LIMIT:
        ratios.append(sharpe)

    end_portfolio_value = cerebro.broker.getvalue()
    pnl = end_portfolio_value - start_portfolio_value
    # print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
    # print(f'Final Portfolio Value: {end_portfolio_value:2f}')
    # print(f'PnL: {pnl:.2f}')
    # print(f'Sharpe: {run[0].analyzers.sharpe_ratio.ratio}')

def calculateHurst(file):
    df = pd.read_csv("../data/" + file)
    filtered = df[(df['Date'] > TRAIN_START_DATE) & (df['Date'] < TRAIN_END_DATE)]
    # log_return = np.log(filtered.Close / filtered.Close.shift(1)).dropna()
    hurst_val = hurst(filtered.Close.values, range(HURST_LAG_LOWER_LIMIT, HURST_LAG_UPPER_LIMIT))
    if hurst_val <= 0.5:
        print("Skipping as hurst < 0.5 " + file)
        return -1
    else:
        print("Calculated Hurst for " + file + " : " + str(hurst_val))
        return hurst_val

def getResults(asset):
    average_sharpe_by_asset = {}
    hurst_by_asset = {}

    for subdir, dirs, files in os.walk("../data/"):
        for file in files:
            if asset not in file:
                continue
            try:
                ratios = []
                hurst_val = calculateHurst(file)

                # Check if series is trending
                if hurst_val == -1:
                    continue

                for pfast in range(MOVING_AVERAGE_FAST, MOVING_AVERAGE_SLOW):
                    for pslow in range(pfast + 10, pfast * MOVING_AVERAGE_UPPER_LIMIT_MULTIPLIER):
                        runBacktest(pfast, pslow, file, ratios)
                calculateAverageSharpeRatio(ratios, average_sharpe_by_asset, file, hurst_val, hurst_by_asset)
            except Exception as e:
                print("Exception parsing " + file+ " : " + str(e))

    df_results = pd.DataFrame({'Symbol': average_sharpe_by_asset.keys(), 'Sharpe Ratio': average_sharpe_by_asset.values(), 'Hurst:': hurst_by_asset.values()})
    df_results.to_csv("momentum_results_" + asset + ".csv")

if __name__ == '__main__':
    getResults("stock")
    getResults("crypto")
    getResults("fx")