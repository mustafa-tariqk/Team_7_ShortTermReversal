class Team7Algo(QCAlgorithm):

    def Initialize(self):
        pass

    def OnSecuritiesChanged(self, changes):
        pass
        
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
        pass
            
class SymbolData():
    pass
