import backtrader as bt

class VolAdjustedSizer(bt.Sizer):
    params = (('target_vol', 0.1),
              ('window_vol', 20),
              ('movav', bt.indicators.MovingAverageExponential))

    def __init__(self):
        self.vol = bt.indicators.StandardDeviation(period=self.p.window_vol, movav=self.p.movav)

    def _getsizing(self, comminfo, cash, data, isbuy):
        size = self.p.target_vol / self.vol[0]
        return size