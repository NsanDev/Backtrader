import backtrader as bt

class Momentum(bt.Indicator):
    params = (('lags', 20),)
    lines = ('momentum',)

    def __init__(self):
        #super(Momentum,self).__init__()
        self.lines.momentum = (self.data - self.data(-self.p.lags))

class MomentumStrategy(bt.SignalStrategy):
    params = (('lags', 20),)

    def __init__(self):
        self.momentum = Momentum
        self.momentum.params.lags = self.params.lags
        self.signal_add(bt.SIGNAL_LONGSHORT, self.momentum())
