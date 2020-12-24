from strategies import *
import backtrader as bt
import datetime
import os
import pandas as pd
from hurst.pair_stocks import *
from hurst.hurst_calculation import *

if __name__ == '__main__':
    data = {}
    df = pd.DataFrame()

    for subdir, dirs, files in os.walk("../data/"):
        for file in files:
            df_cur = pd.read_csv("../data/" + file)
            filtered = df_cur[(df_cur['Date'] > '2019-01-01') & (df_cur['Date'] < '2019-12-01')]
            df[file.split('_')[1]] = filtered['Close'].values
            data.setdefault(file.split("_")[0], []).append(file)

    scores, p_values, pairs = find_cointegrated_pairs(df)

    for i, file1 in enumerate(data['stock']):
        for j, file2 in enumerate(data['stock']):
            if i == j:
                continue

            df1 = pd.read_csv("../data/" + file1)
            filtered1 = df1[(df1['Date'] > '2019-01-01') & (df1['Date'] < '2019-12-01')]

            df2 = pd.read_csv("../data/" + file2)
            filtered2 = df2[(df2['Date'] > '2019-01-01') & (df2['Date'] < '2019-12-01')]

            df2['ratio'] = df1['Close']/df2['Close']
            hurst_val = hurst(df2['ratio'].values, range(2, 20))
            if hurst_val >= 0.5:
                print("Skipping as hurst > 0.5 " + file1 + "/" + file2)
                continue
            else:
                print("Calculated Hurst for pair " + file1 + "/" + file2 + " : " + str(hurst_val))

            symbol1 = file1.split('_')[1]
            symbol2 = file2.split('_')[1]

            if (symbol1, symbol2) not in pairs and (symbol2, symbol1) not in pairs:
                print("Skipping pair " + str((symbol1, symbol2)) + " as it is not found to be cointegrated")
                continue

            ratios = {}

            cerebro = bt.Cerebro()

            data1 = bt.feeds.YahooFinanceCSVData(
                dataname='../data/' + file1,
                fromdate=datetime.datetime(2016, 1, 1),
                todate=datetime.datetime(2017, 12, 25),
            )

            data2 = bt.feeds.YahooFinanceCSVData(
                dataname='../data/' + file2,
                fromdate=datetime.datetime(2016, 1, 1),
                todate=datetime.datetime(2017, 12, 25),
            )

            cerebro.adddata(data1)
            cerebro.adddata(data2)
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
            cerebro.addsizer(bt.sizers.SizerFix, stake=3)
            start_portfolio_value = cerebro.broker.getvalue()
            cerebro.addstrategy(PairTradingStrategy)

            run = cerebro.run()
            sharpe = run[0].analyzers.sharpe_ratio.ratio
            #cerebro.plot()

            end_portfolio_value = cerebro.broker.getvalue()
            pnl = end_portfolio_value - start_portfolio_value
            print("Calculated sharpe " + str(sharpe) + " for pair " + symbol1 + "/" + symbol2)
            #print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
            #print(f'Final Portfolio Value: {end_portfolio_value:2f}')
            #print(f'PnL: {pnl:.2f}')
            #print(f'Sharpe: {}')