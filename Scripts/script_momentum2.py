import datetime  # For datetime objects

# Import the backtrader platform
import backtrader as bt
import pandas as pd
import pytz

from Providers.lim import fetch_contract, COLUMN_NAMES


class MomentumStrategy(bt.SignalStrategy):
    params = (('lags', 120),)

    def __init__(self):
        # self.addminperiod(self.params.lags)
        self.vol = bt.indicators.StandardDeviation(period=10,
                                                   movav=bt.indicators.MovingAverageExponential)
        self.momentum = (self.data - self.data(-self.params.lags))  # /self.vol
        self.signal_add(bt.SIGNAL_LONGSHORT, self.momentum)

# works only for Momentum strategy which has parameter vol
class VolAdjustedSizer(bt.Sizer):
    params = (('target_vol', 0.1),
              ('window_vol', 20),
              ('movav',bt.indicators.MovingAverageExponential))

    def __init__(self):
        self.vol = bt.indicators.StandardDeviation(period=self.p.window_vol, movav=self.p.movav)

    def _getsizing(self, comminfo, cash, data, isbuy):
        size = self.p.target_vol/self.vol[0]
        return int(size)

# Create a cerebro entity

# cerebro.addanalyzer(bt.analyzers.PyFolio)
# cerebro.addstrategy(MomentumStrategy, lag=20)

df = fetch_contract('CL_2015Z', COLUMN_NAMES, '2012-01-01', '2015-01-01')
# Create a Data Feed
data = bt.feeds.PandasData(
    dataname=df,
    # Do not pass values before this date
    fromdate=datetime.datetime(2012, 1, 1, tzinfo=pytz.utc),
    # Do not pass values after this date
    todate=datetime.datetime(2015, 1, 1, tzinfo=pytz.utc))

ALL_LAGS = [5, 20, 60, 120, 252]
strats = []
all_returns = pd.DataFrame()
all_positions = pd.DataFrame()
all_positions["cash"] = 0
all_transactions = pd.DataFrame()
all_gross_levs = pd.DataFrame()

for i in range(len(ALL_LAGS)):
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.broker.setcash(1000.0)  # Set our desired cash start
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    cerebro.addstrategy(MomentumStrategy, lags=ALL_LAGS[i])
    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addsizer(VolAdjustedSizer)
    # cerebro.signal_concurrent(True)
    # Add a FixedSize sizer according to the stake
    # cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    # Set the commission
    # cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    strats.append(cerebro.run()[0])  # runonce=False)
    # Run over everything
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()

    pyfoliozer = strats[i].analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    all_returns[str(ALL_LAGS[i])] = returns
    all_positions[str(ALL_LAGS[i])] = positions['Data0']
    all_positions['cash'] = all_positions['cash'] + positions['cash']

    # Print out the final result