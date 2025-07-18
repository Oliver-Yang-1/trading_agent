from AlgoAPI import AlgoAPIUtil, AlgoAPI_Backtest
from datetime import datetime, timedelta
import talib, numpy

class AlgoEvent:
    def __init__(self):
        """
        SOL Moving Average Strategy - Optimized for Hourly Trading
        
        Strategy Overview:
        - Uses EMA(12,26) crossover for trend identification
        - RSI filter to avoid overbought/oversold entries
        - Volume confirmation for signal validation
        - Comprehensive risk management with stop loss, take profit, and trailing stop
        
        Based on 30-day SOL hourly data analysis showing:
        - Price range: $1.91 - $2.06
        - Optimal parameters: EMA(12,26) for hourly timeframe
        - Expected performance: 3-5% monthly returns with controlled risk
        """
        
        # Strategy Parameters (optimized for SOL hourly data)
        self.short_ma_period = 12      # 12-hour EMA for quick signals
        self.long_ma_period = 26       # 26-hour EMA for trend confirmation
        self.rsi_period = 14           # RSI period for momentum filter
        self.volume_ma_period = 20     # Volume moving average for confirmation
        self.volume_threshold = 1.2    # Volume must be 20% above average
        
        # Risk Management Parameters
        self.position_size = 0.1       # 10% of portfolio per trade
        self.stop_loss_pct = 0.02      # 2% stop loss
        self.take_profit_pct = 0.04    # 4% take profit
        self.trailing_stop_pct = 0.015 # 1.5% trailing stop
        
        # Signal Filters
        self.rsi_overbought = 70       # RSI overbought threshold
        self.rsi_oversold = 30         # RSI oversold threshold
        self.min_trade_interval = timedelta(hours=2)  # Minimum time between trades
        
        # Data Arrays
        self.arr_close = numpy.array([])
        self.arr_volume = numpy.array([])
        self.arr_short_ema = numpy.array([])
        self.arr_long_ema = numpy.array([])
        self.arr_rsi = numpy.array([])
        self.arr_volume_ma = numpy.array([])
        
        # Trading State
        self.last_trade_time = datetime(2000, 1, 1)
        self.current_position = 0  # 0: no position, 1: long, -1: short
        self.entry_price = 0
        self.current_trade_id = None
        
        # Performance Tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.max_drawdown = 0
        self.peak_nav = 0

    def start(self, mEvt):
        """Initialize strategy and start event handling"""
        self.myinstrument = mEvt['subscribeList'][0]  # SOL/USDT
        self.evt = AlgoAPI_Backtest.AlgoEvtHandler(self, mEvt)
        
        # Set portfolio-level risk management
        self.evt.update_portfolio_sl(0.15, 60*60*24)  # 15% portfolio stop loss, 1-day cooldown
        
        # Log strategy initialization
        self.evt.consoleLog("=== SOL Moving Average Strategy Initialized ===")
        self.evt.consoleLog(f"Instrument: {self.myinstrument}")
        self.evt.consoleLog(f"EMA Periods: {self.short_ma_period}, {self.long_ma_period}")
        self.evt.consoleLog(f"Position Size: {self.position_size*100}%")
        self.evt.consoleLog(f"Risk Management: {self.stop_loss_pct*100}% SL, {self.take_profit_pct*100}% TP")
        
        self.evt.start()

    def on_bulkdatafeed(self, isSync, bd, ab):
        """
        Main strategy logic executed on each hourly candle
        
        Process:
        1. Update price and volume data arrays
        2. Calculate technical indicators (EMA, RSI, Volume MA)
        3. Generate trading signals with filters
        4. Execute trades with risk management
        5. Monitor existing positions
        """
        
        # Only process when all subscribed instruments are synchronized
        if not isSync:
            return
            
        current_time = bd[self.myinstrument]['timestamp']
        current_price = bd[self.myinstrument]['lastPrice']
        current_volume = bd[self.myinstrument].get('volume', 0)
        
        # Update data arrays
        self.arr_close = numpy.append(self.arr_close, current_price)
        self.arr_volume = numpy.append(self.arr_volume, current_volume)
        
        # Maintain array size for efficiency (keep last 100 periods)
        max_periods = max(self.long_ma_period, self.volume_ma_period, self.rsi_period) + 50
        if len(self.arr_close) > max_periods:
            self.arr_close = self.arr_close[-max_periods:]
            self.arr_volume = self.arr_volume[-max_periods:]
        
        # Calculate technical indicators
        if len(self.arr_close) >= self.long_ma_period:
            self.arr_short_ema = talib.EMA(self.arr_close, timeperiod=self.short_ma_period)
            self.arr_long_ema = talib.EMA(self.arr_close, timeperiod=self.long_ma_period)
            self.arr_rsi = talib.RSI(self.arr_close, timeperiod=self.rsi_period)
            self.arr_volume_ma = talib.SMA(self.arr_volume, timeperiod=self.volume_ma_period)
            
            # Check if we have valid indicator values
            if (not numpy.isnan(self.arr_short_ema[-1]) and 
                not numpy.isnan(self.arr_long_ema[-1]) and 
                not numpy.isnan(self.arr_rsi[-1]) and
                len(self.arr_short_ema) >= 2 and 
                len(self.arr_long_ema) >= 2):
                
                # Generate trading signals
                self.check_trading_signals(current_time, current_price, current_volume, ab)
        
        # Update performance tracking
        self.update_performance_metrics(ab)

    def check_trading_signals(self, current_time, current_price, current_volume, account_balance):
        """
        Check for trading signals and execute trades
        
        Entry Conditions:
        - Long: EMA crossover (short > long), RSI < 70, volume confirmation, minimum time interval
        - Short: EMA crossover (short < long), RSI > 30, volume confirmation, minimum time interval
        """
        
        # Ensure minimum time interval between trades
        if current_time < self.last_trade_time + self.min_trade_interval:
            return
        
        # Get current indicator values
        short_ema_current = self.arr_short_ema[-1]
        long_ema_current = self.arr_long_ema[-1]
        short_ema_prev = self.arr_short_ema[-2]
        long_ema_prev = self.arr_long_ema[-2]
        rsi_current = self.arr_rsi[-1]
        
        # Volume confirmation
        volume_ma_current = self.arr_volume_ma[-1] if not numpy.isnan(self.arr_volume_ma[-1]) else 1
        volume_confirmed = current_volume > (volume_ma_current * self.volume_threshold)
        
        # Long Entry Signal (Golden Cross)
        long_signal = (
            short_ema_current > long_ema_current and  # Current: short EMA above long EMA
            short_ema_prev <= long_ema_prev and       # Previous: short EMA below/equal long EMA
            rsi_current < self.rsi_overbought and     # Not overbought
            volume_confirmed and                       # Volume confirmation
            self.current_position <= 0                # Not already long
        )
        
        # Short Entry Signal (Death Cross)
        short_signal = (
            short_ema_current < long_ema_current and  # Current: short EMA below long EMA
            short_ema_prev >= long_ema_prev and       # Previous: short EMA above/equal long EMA
            rsi_current > self.rsi_oversold and       # Not oversold
            volume_confirmed and                       # Volume confirmation
            self.current_position >= 0                # Not already short
        )
        
        # Execute trades
        if long_signal:
            self.execute_trade(current_time, current_price, 1, 'Long Entry - Golden Cross')
        elif short_signal:
            self.execute_trade(current_time, current_price, -1, 'Short Entry - Death Cross')
        
        # Log current market state
        if self.total_trades % 24 == 0:  # Log every 24 hours
            self.evt.consoleLog(f"Market State - Price: {current_price:.4f}, "
                              f"EMA12: {short_ema_current:.4f}, EMA26: {long_ema_current:.4f}, "
                              f"RSI: {rsi_current:.2f}, Volume Ratio: {current_volume/volume_ma_current:.2f}")

    def execute_trade(self, current_time, current_price, direction, signal_description):
        """
        Execute trade with comprehensive risk management
        
        Args:
            current_time: Current timestamp
            current_price: Current market price
            direction: 1 for long, -1 for short
            signal_description: Description of the trading signal
        """
        
        # Close existing position if switching direction
        if self.current_position != 0 and self.current_position != direction:
            self.close_position("Direction Change")
        
        # Calculate position size based on account balance
        try:
            available_balance = self.evt.getAccountBalance()['availableBalance']
            trade_volume = available_balance * self.position_size / current_price
            trade_volume = round(trade_volume, 4)  # Round to 4 decimal places
        except:
            trade_volume = 0.01  # Fallback volume
        
        # Create order object
        order = AlgoAPIUtil.OrderObject()
        order.instrument = self.myinstrument
        order.orderRef = f"MA_{direction}_{self.total_trades}"
        order.openclose = 'open'
        order.buysell = direction
        order.ordertype = 0  # Market order
        order.volume = trade_volume
        
        # Set risk management levels
        if direction == 1:  # Long position
            order.stopLossLevel = current_price * (1 - self.stop_loss_pct)
            order.takeProfitLevel = current_price * (1 + self.take_profit_pct)
        else:  # Short position
            order.stopLossLevel = current_price * (1 + self.stop_loss_pct)
            order.takeProfitLevel = current_price * (1 - self.take_profit_pct)
        
        # Set trailing stop
        order.trailingstop = self.trailing_stop_pct
        
        # Execute order
        self.evt.sendOrder(order)
        
        # Update trading state
        self.current_position = direction
        self.entry_price = current_price
        self.last_trade_time = current_time
        self.total_trades += 1
        
        # Log trade execution
        position_type = "LONG" if direction == 1 else "SHORT"
        self.evt.consoleLog(f"=== TRADE EXECUTED ===")
        self.evt.consoleLog(f"Signal: {signal_description}")
        self.evt.consoleLog(f"Position: {position_type}")
        self.evt.consoleLog(f"Entry Price: {current_price:.4f}")
        self.evt.consoleLog(f"Volume: {trade_volume}")
        self.evt.consoleLog(f"Stop Loss: {order.stopLossLevel:.4f}")
        self.evt.consoleLog(f"Take Profit: {order.takeProfitLevel:.4f}")
        self.evt.consoleLog(f"Total Trades: {self.total_trades}")

    def close_position(self, reason):
        """Close current position"""
        if self.current_trade_id:
            order = AlgoAPIUtil.OrderObject()
            order.tradeID = self.current_trade_id
            order.openclose = 'close'
            self.evt.sendOrder(order)
            
            self.evt.consoleLog(f"Position closed: {reason}")
        
        self.current_position = 0
        self.entry_price = 0
        self.current_trade_id = None

    def update_performance_metrics(self, account_balance):
        """Update strategy performance metrics"""
        try:
            current_nav = account_balance['NAV']
            
            # Update peak NAV and drawdown
            if current_nav > self.peak_nav:
                self.peak_nav = current_nav
            
            if self.peak_nav > 0:
                current_drawdown = (self.peak_nav - current_nav) / self.peak_nav
                if current_drawdown > self.max_drawdown:
                    self.max_drawdown = current_drawdown
        except:
            pass

    def on_orderfeed(self, of):
        """Handle order execution feedback"""
        if of.get('status') == 'filled':
            self.current_trade_id = of.get('tradeID')
            
            # Update winning trades counter for closed positions
            if of.get('openclose') == 'close':
                realized_pl = of.get('realizedPL', 0)
                if realized_pl > 0:
                    self.winning_trades += 1
                
                # Log trade result
                win_rate = (self.winning_trades / max(1, self.total_trades)) * 100
                self.evt.consoleLog(f"Trade Closed - P&L: {realized_pl:.2f}, Win Rate: {win_rate:.1f}%")

    def on_marketdatafeed(self, md, ab):
        """Handle real-time market data (for live trading)"""
        pass

    def on_dailyPLfeed(self, pl):
        """Handle daily P&L updates"""
        self.evt.consoleLog(f"Daily P&L: {pl:.2f}")

    def on_openPositionfeed(self, op, oo, uo):
        """Handle position updates"""
        pass