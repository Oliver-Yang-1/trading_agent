from AlgoAPI import AlgoAPIUtil, AlgoAPI_Backtest
from datetime import datetime, timedelta
import collections

class AlgoEvent:
    """
    Test moving average strategy for testing
    
    Strategy: test_moving_average
    Generated: 2025-07-17 23:34:22
    """
    def __init__(self):
        """
        Initialize strategy parameters
        """
        self.short_window = 10
        self.long_window = 30
        self.volume = 0.01
        
        # Price history for moving averages
        self.price_history = collections.deque(maxlen=max(self.short_window, self.long_window))
        self.position = 0  # Track current position
        self.current_trade_id = None

    def start(self, mEvt):
        """
        Strategy startup function
        
        Args:
            mEvt: Event configuration dictionary
        """
        self.evt = AlgoAPI_Backtest.AlgoEvtHandler(self, mEvt)
        self.evt.start()

    def on_bulkdatafeed(self, isSync, bd, ab):
        """
        Bulk data feed callback
        
        Args:
            isSync: Whether data is synchronized
            bd: Bulk market data dictionary
            ab: Account balance information
        """
        pass

    def on_marketdatafeed(self, md, ab):
        """
        Market data feed callback - executes moving average strategy
        
        Args:
            md: Market data object with timestamp, bidPrice, askPrice
            ab: Account balance information
        """
        # Use mid price for moving average calculation
        mid_price = (md.bidPrice + md.askPrice) / 2
        self.price_history.append(mid_price)
        
        # Need sufficient history for both moving averages
        if len(self.price_history) < self.long_window:
            return
            
        # Calculate moving averages
        short_ma = sum(list(self.price_history)[-self.short_window:]) / self.short_window
        long_ma = sum(list(self.price_history)[-self.long_window:]) / self.long_window
        
        # Trading signals
        if short_ma > long_ma and self.position <= 0:
            # Buy signal
            if self.position < 0:
                self.close_position(md)
            self.open_position(md, 1)  # Buy
            
        elif short_ma < long_ma and self.position >= 0:
            # Sell signal
            if self.position > 0:
                self.close_position(md)
            self.open_position(md, -1)  # Sell

    def open_position(self, md, buysell):
        """
        Open a new position
        
        Args:
            md: Market data object
            buysell: 1 for buy, -1 for sell
        """
        try:
            orderObj = AlgoAPIUtil.OrderObject()
            orderObj.instrument = md.instrument
            orderObj.openclose = 'open'
            orderObj.buysell = buysell
            orderObj.ordertype = 0  # Market order
            orderObj.volume = self.volume
            
            self.evt.sendOrder(orderObj)
            self.position = buysell
        except Exception as e:
            print(f"Error opening position: {str(e)}")

    def close_position(self, md):
        """
        Close current position
        
        Args:
            md: Market data object
        """
        if self.position == 0 or self.current_trade_id is None:
            return
            
        try:
            orderObj = AlgoAPIUtil.OrderObject()
            orderObj.instrument = md.instrument
            orderObj.openclose = 'close'
            orderObj.tradeID = self.current_trade_id
            orderObj.ordertype = 0  # Market order
            orderObj.volume = abs(self.volume)
            
            self.evt.sendOrder(orderObj)
            self.position = 0
            self.current_trade_id = None
        except Exception as e:
            print(f"Error closing position: {str(e)}")

    def on_orderfeed(self, of):
        """
        Order feed callback
        
        Args:
            of: Order feed object
        """
        if of.openclose == 'open' and of.status == 'filled':
            self.current_trade_id = of.tradeID

    def on_dailyPLfeed(self, pl):
        """
        Daily P&L feed callback
        
        Args:
            pl: P&L information
        """
        pass

if __name__ == "__main__":
    pass
