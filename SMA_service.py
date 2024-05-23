from pyalgotrade.barfeed import csvfeed
from pyalgotrade import strategy
from pyalgotrade.bar import Frequency
from pyalgotrade.technical import ma
from pyalgotrade.stratanalyzer import returns
from pyalgotrade import plotter
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades
from output_service import OutputStatistics
import csv


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod, csvInstance=None):
        super(MyStrategy, self).__init__(feed, 1000000)
        self.__position = None
        self.__instrument = instrument
        # We'll use adjusted close values instead of regular close values.
        # self.setUseAdjustedValues(True)
        self.__sma = ma.SMA(feed[instrument].getPriceDataSeries(), smaPeriod)
        self.csvInstance = csvInstance

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at %.2f" % (execInfo.getPrice()))
        print("Buy Time {0}".format(self.getCurrentDateTime()))
        self.csvInstance.writerow(
            [self.getCurrentDateTime(), "BUY", execInfo.getPrice()]
        )

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        print("SELL at %.2f" % (execInfo.getPrice()))
        self.info("SELL at %.2f" % (execInfo.getPrice()))
        self.csvInstance.writerow(
            [self.getCurrentDateTime(), "SELL", execInfo.getPrice()]
        )
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
            return

        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if bar.getPrice() > self.__sma[-1]:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
                
        # Check if we have to exit the position.
        elif bar.getPrice() < self.__sma[-1] and not self.__position.exitActive():
            self.__position.exitMarket()

"""         if self.__sma[-1] is None:
            return

        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if bar.getPrice() > self.__sma[-1]:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
            elif bar.getPrice() < self.__sma[-1]:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterShort(self.__instrument, 10, True)
        # Check if we have to exit the position.
        elif (bar.getPrice() < self.__sma[-1] or bar.getPrice() < self.__sma[-1]) and not self.__position.exitActive():
            self.__position.exitMarket() """



""" TODO: Sharpe ratio, drawdowns, Drawdown sequences, Win % and Loss % max drawdown,
min drawdon, k ratio
1. Need context abt the period for calculaion of the Current Rate of Return, figuring out the monthly 
rate of return while strat runs is still wip, or can it be daily?
, max loss and max profit, kelly criteria,Add slippages if possible,

 TDLR: STOP loss (% and price limit(-ve/+ve s.d delta)),
 check for multiple SMA's

 1. Binning for Daily and Weekly
 2. Ratios calculation
 3. Partial integration for Bins in the Logic
 4. Simple charting
 
TO DO

1. Integration of DS's
2. K-ratio
3. Chart clarity
4. Finding out week based/ Custom date info for the calculations
   
     """


def run_strategy(smaPeriod):
    feed = csvfeed.GenericBarFeed(Frequency.MINUTE)
    feed.addBarsFromCSV("nifty", "./1hourniftychart.csv")
    # Evaluate the strategy with the feed's bars.
    # open the file in the write mode
    f = open("./csv_file_long_only", "w")
    # create the csv writer
    writer = csv.writer(f)
    writer.writerow(["DATE", "TRADE", "PRICE"])
    myStrategy = MyStrategy(feed, "nifty", smaPeriod, writer)
    print("Final portfolio value: %.2f" % myStrategy.getBroker().getEquity())

    # Attach different analyzers to a strategy before executing it.
    retAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(retAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    myStrategy.attachAnalyzer(sharpeRatioAnalyzer)
    drawDownAnalyzer = drawdown.DrawDown()
    myStrategy.attachAnalyzer(drawDownAnalyzer)
    tradesAnalyzer = trades.Trades()
    myStrategy.attachAnalyzer(tradesAnalyzer)

    plt = plotter.StrategyPlotter(myStrategy)

    plt.getOrCreateSubplot("returns").addDataSeries(
        "Simple returns", retAnalyzer.getReturns()
    )
    myStrategy.run()
    myStrategy.info("Final portfolio value: ₹%.2f" % myStrategy.getResult())
    # Plot the strategy.
    plt.plot()
    plt.savePlot('nifty1hourplot',300)
    output_stats = OutputStatistics(
        myStrategy, tradesAnalyzer,  sharpeRatioAnalyzer, retAnalyzer, drawDownAnalyzer,writer
    )
    output_stats.overall_analysis()
    output_stats.ratio_printer()
    output_stats.profitable_trades()
    output_stats.unprofitable_trades()
    f.close()


run_strategy(9)
