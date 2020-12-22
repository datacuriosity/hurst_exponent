from strategies import *
import backtrader as bt
import datetime

if __name__ == '__main__':
    ratios = {}

    for pfast in range(10, 50):
        for pslow in range(pfast + 10, pfast * 2):
            cerebro = bt.Cerebro()

            data = bt.feeds.YahooFinanceCSVData(
                dataname='data/TSLA.csv',
                fromdate=datetime.datetime(2016, 1, 1),
                todate=datetime.datetime(2017, 12, 25),
            )

            print(str(pfast)+","+str(pslow))
            cerebro.adddata(data)
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
            cerebro.addsizer(bt.sizers.SizerFix, stake=3)
            start_portfolio_value = cerebro.broker.getvalue()
            cerebro.addstrategy(MAcrossover, pfast=pfast, pslow=pslow)

            run = cerebro.run()
            sharpe = run[0].analyzers.sharpe_ratio.ratio
            ratios[(pfast, pslow)] = sharpe
            #cerebro.plot()

            end_portfolio_value = cerebro.broker.getvalue()
            pnl = end_portfolio_value - start_portfolio_value
            #print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
            #print(f'Final Portfolio Value: {end_portfolio_value:2f}')
            #print(f'PnL: {pnl:.2f}')
            #print(f'Sharpe: {run[0].analyzers.sharpe_ratio.ratio}')

print(sorted(ratios.items(), key=lambda x: x[1], reverse=True))