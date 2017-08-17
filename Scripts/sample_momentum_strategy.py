import backtrader as bt
import Strategies.MomentumStrategy as ms
from Providers.lim import fetch_contract, COLUMN_NAMES, fetch_continuous_contract
from Sizers.VolSizers import VolAdjustedSizer


ticker = 'CL'
from_date = '2012-01-01'
to_date = '2015-01-01'

df = fetch_contract('CL_2015Z', COLUMN_NAMES, from_date, to_date) # fetch from lim
#benchmark = fetch_continuous_contract(ticker, COLUMN_NAMES, from_date, to_date)
# Create a Data Feed
df = df.tz_localize('UTC', level=0)
data = bt.feeds.PandasData(
    dataname=df,
    # Do not pass values before this date
    fromdate=df.index[0],
    # Do not pass values after this date
    todate=df.index[-1])


cerebro = bt.Cerebro()
cerebro.addstrategy(ms.MomentumStrategy, lags=50) # Add strategy with its parameters lags
cerebro.addsizer(VolAdjustedSizer, target_vol=0.1, window_vol=20) # How much we
cerebro.adddata(data)
cerebro.broker.setcash(1000.0)  # Set our desired cash start

cerebro.addobserver(bt.observers.DrawDown) #Drawown will be calculated and plotted by Cerebro
cerebro.addanalyzer(bt.analyzers.PyFolio)
cerebro.addanalyzer(bt.analyzers.SharpeRatio,riskfreerate=0.01,annualize=True)

strat = cerebro.run()
pyfoliozer = strat[0].analyzers.getbyname('pyfolio')
sharpe_ratio = strat[0].analyzers.sharperatio.ratio

print(f"The sharp ratio of this strategy is {sharpe_ratio}")

cerebro.plot()
