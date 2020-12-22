from strategies import *
import backtrader as bt
import datetime

if __name__ == '__main__':
    ratios = {}

    cerebro = bt.Cerebro()

    data1 = bt.feeds.YahooFinanceCSVData(
        dataname='data/stockAAPL_from_2000-01-01_to_2020-11-18.csv',
        fromdate=datetime.datetime(2016, 1, 1),
        todate=datetime.datetime(2017, 12, 25),
    )

    data2 = bt.feeds.YahooFinanceCSVData(
        dataname='TSLA.csv',
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
    print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
    print(f'Final Portfolio Value: {end_portfolio_value:2f}')
    print(f'PnL: {pnl:.2f}')
    print(f'Sharpe: {run[0].analyzers.sharpe_ratio.ratio}')