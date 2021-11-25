class Team7Algo(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2000, 1, 1)  
        self.SetCash(100000)

        self.symbol = self.AddEquity('SPY', Resolution.Daily).Symbol
        
        self.coarse_count = 500
        self.stock_selection = 10
        self.top_by_market_cap_count = 100
        
        self.period = 21
        
        self.long = []
        self.short = []
        
        # Daily close data
        self.data = {}
        
        self.day = 1
        self.selection_flag = False
        self.UniverseSettings.Resolution = Resolution.Daily
        self.AddUniverse(self.CoarseSelectionFunction, self.FineSelectionFunction)
        self.Schedule.On(self.DateRules.EveryDay(self.symbol), self.TimeRules.AfterMarketOpen(self.symbol), self.Selection)
        
    def CoarseSelectionFunction(self, coarse):
        for stock in coarse:
            symbol = stock.Symbol

            if symbol in self.data:
                self.data[symbol].update(stock.AdjustedPrice)

        if not self.selection_flag:
            return Universe.Unchanged

        selected = sorted([x for x in coarse if x.HasFundamentalData and x.Market == 'usa' and x.Price > 1],
            key=lambda x: x.DollarVolume, reverse=True)
        selected = [x.Symbol for x in selected][:self.coarse_count]

        for symbol in selected:
            if symbol in self.data:
                continue

            self.data[symbol] = SymbolData(self.period)
            history = self.History(symbol, self.period, Resolution.Daily)
            if history.empty:
                self.Log(f"Not enough data for {symbol} yet")
                continue
            closes = history.loc[symbol].close
            for time, close in closes.iteritems():
                self.data[symbol].update(close)

        return [x for x in selected if self.data[x].is_ready()]

    def FineSelection(self, fine):
        pass
    
    def OnData(self, data):
        pass
                
    def Selection(self):
        if self.day == 5:
            self.selection_flag = True
        
        self.day += 1
        if self.day > 5:
            self.day = 1
            
class SymbolData():
    def __init__(self, period):
        self.closes = RollingWindow[float](13)
        self.period = period
    
    def update(self, close):
        self.closes.Add(close)

    def is_ready(self):
        return self.closes.IsReady

    def weekly_return(self):
        return self.closes[0] / self.closes[4] -1

    def monthly_return(self):
        return self.closes[0] / self.closes[self.period] -1
