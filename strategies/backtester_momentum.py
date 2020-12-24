import backtrader as bt
import datetime
import os
import pandas as pd
from hurst.hurst_calculation import *
from strategies import *

if __name__ == '__main__':
    results = {}

    for subdir, dirs, files in os.walk("../data/"):
        for file in files:
            ratios = []

            df = pd.read_csv("../data/" + file)
            filtered = df[(df['Date'] > '2019-01-01') & (df['Date'] < '2019-12-01')]
            hurst_val = hurst(filtered['Close'].values, range(2, 20))
            if hurst_val <= 0.5:
                print("Skipping as hurst < 0.5 " + file)
                continue
            else:
                print("Calculated Hurst for " + file + " : " + str(hurst_val))

            for pfast in range(10, 15):
                for pslow in range(pfast + 10, pfast * 2):
                    cerebro = bt.Cerebro()

                    data = bt.feeds.YahooFinanceCSVData(
                        dataname='../data/' + file,
                        fromdate=datetime.datetime(2016, 1, 1),
                        todate=datetime.datetime(2017, 12, 25),
                    )

                    cerebro.adddata(data)
                    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
                    cerebro.addsizer(bt.sizers.AllInSizer)
                    start_portfolio_value = cerebro.broker.getvalue()
                    cerebro.addstrategy(MAcrossover, pfast=pfast, pslow=pslow)

                    run = cerebro.run()
                    sharpe = run[0].analyzers.sharpe_ratio.ratio
                    if sharpe and sharpe > 0.0 and sharpe < 4.0:
                        ratios.append(sharpe)
                    #cerebro.plot()

                    end_portfolio_value = cerebro.broker.getvalue()
                    pnl = end_portfolio_value - start_portfolio_value
                    #print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
                    #print(f'Final Portfolio Value: {end_portfolio_value:2f}')
                    #print(f'PnL: {pnl:.2f}')
                    #print(f'Sharpe: {run[0].analyzers.sharpe_ratio.ratio}')

            if len(ratios) > 0:
                avg_sharpe = sum(ratios) / len(ratios)
                print(file + " has average sharpe " + str(avg_sharpe))
                results[file.split('_')[1]] = avg_sharpe
            else:
                print("No suitable sharpe found for " + file)

    df_results = pd.DataFrame({'Symbol': results.keys(), 'Sharpe Ratio': results.values()})
    df_results.to_csv("momentum_results.csv")