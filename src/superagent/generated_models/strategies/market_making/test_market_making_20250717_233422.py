from AlgoAPI import AlgoAPIUtil, AlgoAPI_Backtest
from datetime import datetime, timedelta

class AlgoEvent:
    """
    Test market making strategy for testing
    
    Strategy: test_market_making
    Generated: 2025-07-17 23:34:22
    """
    def __init__(self):
        """
        Initialize strategy parameters
        """
        self.lasttradetime = datetime(2000, 1, 1)
        self.spread = 0.01
        self.volume = 0.05
        self.trade_interval_hours = 24

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
        Market data feed callback - executes market making strategy
        
        Args:
            md: Market data object with timestamp, bidPrice, askPrice
            ab: Account balance information
        """
        if md.timestamp >= self.lasttradetime + timedelta(hours=self.trade_interval_hours):
            # Calculate bid and ask prices based on spread
            mid_price = (md.bidPrice + md.askPrice) / 2
            bid_price = mid_price - (self.spread / 2)
            ask_price = mid_price + (self.spread / 2)
            
            # Place buy limit order
            self.place_limit_order(md, 1, bid_price, 'open')
            
            # Place sell limit order
            self.place_limit_order(md, -1, ask_price, 'open')
            
            self.lasttradetime = md.timestamp

    def place_limit_order(self, md, buysell, price, openclose):
        """
        Place a limit order
        
        Args:
            md: Market data object
            buysell: 1 for buy, -1 for sell
            price: Order price
            openclose: 'open' or 'close'
        """
        try:
            orderObj = AlgoAPIUtil.OrderObject()
            orderObj.instrument = md.instrument
            orderObj.openclose = openclose
            orderObj.buysell = buysell
            orderObj.ordertype = 1  # Limit order
            orderObj.volume = self.volume
            orderObj.price = price
            
            self.evt.sendOrder(orderObj)
        except Exception as e:
            print(f"Error placing order: {str(e)}")

    def on_orderfeed(self, of):
        """
        Order feed callback
        
        Args:
            of: Order feed object
        """
        pass

    def on_dailyPLfeed(self, pl):
        """
        Daily P&L feed callback
        
        Args:
            pl: P&L information
        """
        pass

if __name__ == "__main__":
    pass
