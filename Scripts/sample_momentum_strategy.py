import datetime  # For datetime objects
import backtrader as bt
import pytz
import Strategies.MomentumStrategy as ms
from Providers.lim import fetch_contract, COLUMN_NAMES, fetch_continuous_contract
from Sizers.VolSizers import VolAdjustedSizer


ticker = 'CL'
from_date = '2015-01-01'
to_date = '2017-01-01'

#df = fetch_contract('CL_2015Z', COLUMN_NAMES, '2012-01-01', '2015-01-01')
df = fetch_continuous_contract(ticker, COLUMN_NAMES, from_date, to_date)
# Create a Data Feed
df = df.tz_localize('UTC', level=0)
data = bt.feeds.PandasData(
    dataname=df,
    # Do not pass values before this date
    fromdate=df.index[0],
    # Do not pass values after this date
    todate=df.index[-1])


cerebro = bt.Cerebro()
cerebro.addstrategy(ms.MomentumStrategy, lags=50)
cerebro.addsizer(VolAdjustedSizer, target_vol=0.1, window_vol=20)
cerebro.adddata(data)
cerebro.broker.setcash(1000.0)  # Set our desired cash start
cerebro.addobserver(bt.observers.DrawDown)
cerebro.run()
cerebro.plot()
