from typing_extensions import TypeGuard


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

    def FineSelect(self, fine):
        
        fine = [x for x in fine if x.MarketCap!=0]
        sorted_by_market_cap = sorted(fine, key = lambda x:x.MarketCap, reverse = True)
        topByMarketcap = [x.Symbol for x in sorted_by_market_cap [:self.top_by_market_cap_count]]
        monthPerformance = {symbol:self.data[symbol].monthly_return() for symbol in topByMarketcap}
        weekPerformance = {symbol:self.data[symbol].weekly_return() for symbol in topByMarketcap}
        sortedmonthPerformance = [x[0] for x in sorted(monthPerformance.items(), key= lambda item: item[1], reverse=True)]
        sortedWeekPerformance = [x[0] for x in sorted(weekPerformance.items(), key= lambda item: item[1])]
        self.long = sortedWeekPerformance[:self.stock_selection]
        for symbol in sortedmonthPerformance:
            if symbol not in self.long:
                self.short.append(symbol)
            if len(self.short)==10:
                break
        return self.long + self.short


        pass

    def FineSelection(self, fine):
        pass
    
    def OnData(self, data):
        if not self.selection_flag:
            return
        self.selection_flag = False

        invested = []

        for x in self.Portfolio:
            if x.Value.Invested:
                invested.append(x.Key)

        for symbol in invested:
            if symbol not in self.short + self.long:
                self.Liquidate(symbol)
        
        for symbol in self.short:
            if self.Securities[symbol].Price != 0 and self.Securities[symbol].IsTradeable:
                self.setHoldings(symbol, -1/len(self.short))

        for symbol in self.long:
            if self.Securities[symbol].Price != 0 and self.Securities[symbol].IsTradeable:
                self.setHoldings(symbol, 1/len(self.long))

        self.short.clear()
        self.long.clear()
                
    def Selection(self):
        if self.day == 5:
            self.selection_flag = True
        
        self.day += 1
        if self.day > 5:
            self.day = 1
    
            
class SymbolData():
    def __init__(self, period):
        self.closes = RollingWindow[float](self.period)
        self.period = period
    
    def update(self, close):
        self.closes.Add(close)

    def is_ready(self):
        return self.closes.IsReady

    def weekly_return(self):
        return self.closes[0] / self.closes[4] -1

    def monthly_return(self):
        return self.closes[0] / self.closes[self.period] -1


