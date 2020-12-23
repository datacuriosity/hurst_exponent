from strategies import *
import backtrader as bt
import datetime
import os
import pandas as pd

if __name__ == '__main__':
    results = {}

    for subdir, dirs, files in os.walk("../data/"):
        for file in files:
            ratios = []

            for pfast in range(10, 15):
                for pslow in range(pfast + 10, pfast * 2):
                    cerebro = bt.Cerebro()

                    data = bt.feeds.YahooFinanceCSVData(
                        dataname='../data/' + file,
                        fromdate=datetime.datetime(2016, 1, 1),
                        todate=datetime.datetime(2017, 12, 25),
                    )

                    print(str(pfast)+","+str(pslow))
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
                    print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
                    print(f'Final Portfolio Value: {end_portfolio_value:2f}')
                    print(f'PnL: {pnl:.2f}')
                    print(f'Sharpe: {run[0].analyzers.sharpe_ratio.ratio}')

            results[file.split('_')[1]] = sum(ratios) / len(ratios)

    df_results = pd.DataFrame({'Symbol': results.keys(), 'Sharpe Ratio': results.values()})
    df_results.to_csv("momentum_results.csv")