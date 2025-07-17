import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from .decorators import log_io

logger = logging.getLogger(__name__)

class AlgogeneCodeGeneratorInput(BaseModel):
    """Input for Algogene code generation."""
    strategy_name: str = Field(description="Name of the trading strategy (e.g., 'market_making', 'moving_average')")
    strategy_type: str = Field(description="Type of strategy (e.g., 'market_making', 'trend_following', 'mean_reversion')")
    description: str = Field(description="Description of what the strategy should do")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Strategy parameters and their values")
    code_content: Optional[str] = Field(default=None, description="Generated code content to save")

class AlgogeneCodeGenerator(BaseTool):
    """Tool for generating and saving Algogene platform backtesting models."""
    
    name: str = "algogene_code_generator"
    description: str = (
        "Generate and save Algogene platform backtesting models. "
        "Can generate code based on strategy descriptions and parameters, "
        "or save provided code content to appropriate folders. "
        "Creates structured folders and follows Algogene platform patterns."
    )
    args_schema: type = AlgogeneCodeGeneratorInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def _get_base_dir(self):
        """Get base directory for generated models."""
        return os.path.join(
            os.path.dirname(__file__), 
            "..", "..", 
            "generated_models"
        )
        
    def _get_strategies_dir(self):
        """Get strategies directory."""
        return os.path.join(self._get_base_dir(), "strategies")
        
    def _get_utils_dir(self):
        """Get utils directory."""
        return os.path.join(self._get_base_dir(), "utils")
        
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        try:
            strategies_dir = self._get_strategies_dir()
            utils_dir = self._get_utils_dir()
            
            os.makedirs(strategies_dir, exist_ok=True)
            os.makedirs(utils_dir, exist_ok=True)
            
            # Create strategy type subdirectories
            strategy_subdirs = ['market_making', 'trend_following', 'mean_reversion', 'arbitrage', 'custom']
            for subdir in strategy_subdirs:
                os.makedirs(os.path.join(strategies_dir, subdir), exist_ok=True)
                
        except Exception as e:
            logger.error(f"Error creating directories: {str(e)}")
    
    def _generate_market_making_strategy(self, strategy_name: str, description: str, parameters: Dict[str, Any]) -> str:
        """Generate market making strategy code."""
        spread = parameters.get('spread', 0.01)
        volume = parameters.get('volume', 0.01)
        trade_interval_hours = parameters.get('trade_interval_hours', 24)
        
        code = f'''from AlgoAPI import AlgoAPIUtil, AlgoAPI_Backtest
from datetime import datetime, timedelta

class AlgoEvent:
    """
    {description}
    
    Strategy: {strategy_name}
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    def __init__(self):
        """
        Initialize strategy parameters
        """
        self.lasttradetime = datetime(2000, 1, 1)
        self.spread = {spread}
        self.volume = {volume}
        self.trade_interval_hours = {trade_interval_hours}

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
            print(f"Error placing order: {{str(e)}}")

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
'''
        return code
    
    def _generate_moving_average_strategy(self, strategy_name: str, description: str, parameters: Dict[str, Any]) -> str:
        """Generate moving average strategy code."""
        short_window = parameters.get('short_window', 10)
        long_window = parameters.get('long_window', 30)
        volume = parameters.get('volume', 0.01)
        
        code = f'''from AlgoAPI import AlgoAPIUtil, AlgoAPI_Backtest
from datetime import datetime, timedelta
import collections

class AlgoEvent:
    """
    {description}
    
    Strategy: {strategy_name}
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    def __init__(self):
        """
        Initialize strategy parameters
        """
        self.short_window = {short_window}
        self.long_window = {long_window}
        self.volume = {volume}
        
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
            print(f"Error opening position: {{str(e)}}")

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
            print(f"Error closing position: {{str(e)}}")

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
'''
        return code
    
    def _generate_custom_strategy(self, strategy_name: str, description: str, parameters: Dict[str, Any]) -> str:
        """Generate a custom strategy template."""
        volume = parameters.get('volume', 0.01)
        
        code = f'''from AlgoAPI import AlgoAPIUtil, AlgoAPI_Backtest
from datetime import datetime, timedelta

class AlgoEvent:
    """
    {description}
    
    Strategy: {strategy_name}
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    def __init__(self):
        """
        Initialize strategy parameters
        """
        self.volume = {volume}
        # Add your custom parameters here
        
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
        # Implement bulk data processing logic here
        pass

    def on_marketdatafeed(self, md, ab):
        """
        Market data feed callback - implement your strategy logic here
        
        Args:
            md: Market data object with timestamp, bidPrice, askPrice
            ab: Account balance information
        """
        # TODO: Implement your trading strategy logic here
        # Example:
        # if your_condition:
        #     self.place_order(md, 1, 'open')  # Buy
        # elif your_other_condition:
        #     self.place_order(md, -1, 'open')  # Sell
        pass

    def place_order(self, md, buysell, openclose, ordertype=0, price=None):
        """
        Place an order
        
        Args:
            md: Market data object
            buysell: 1 for buy, -1 for sell
            openclose: 'open' or 'close'
            ordertype: 0 for market, 1 for limit, 2 for stop
            price: Order price (required for limit/stop orders)
        """
        try:
            orderObj = AlgoAPIUtil.OrderObject()
            orderObj.instrument = md.instrument
            orderObj.openclose = openclose
            orderObj.buysell = buysell
            orderObj.ordertype = ordertype
            orderObj.volume = self.volume
            
            if price is not None:
                orderObj.price = price
            
            self.evt.sendOrder(orderObj)
        except Exception as e:
            print(f"Error placing order: {{str(e)}}")

    def on_orderfeed(self, of):
        """
        Order feed callback
        
        Args:
            of: Order feed object
        """
        # Handle order status updates here
        pass

    def on_dailyPLfeed(self, pl):
        """
        Daily P&L feed callback
        
        Args:
            pl: P&L information
        """
        # Handle daily P&L updates here
        pass

if __name__ == "__main__":
    pass
'''
        return code
    
    def _generate_code(self, strategy_name: str, strategy_type: str, description: str, parameters: Dict[str, Any]) -> str:
        """Generate code based on strategy type."""
        if parameters is None:
            parameters = {}
            
        if strategy_type == 'market_making':
            return self._generate_market_making_strategy(strategy_name, description, parameters)
        elif strategy_type == 'trend_following' or strategy_type == 'moving_average':
            return self._generate_moving_average_strategy(strategy_name, description, parameters)
        else:
            return self._generate_custom_strategy(strategy_name, description, parameters)
    
    def _save_code(self, code: str, strategy_name: str, strategy_type: str) -> str:
        """Save generated code to appropriate folder."""
        try:
            # Ensure directories exist
            self._ensure_directories()
            
            strategies_dir = self._get_strategies_dir()
            
            # Determine target directory
            if strategy_type in ['market_making', 'trend_following', 'mean_reversion', 'arbitrage']:
                target_dir = os.path.join(strategies_dir, strategy_type)
            else:
                target_dir = os.path.join(strategies_dir, 'custom')
            
            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{strategy_name}_{timestamp}.py"
            filepath = os.path.join(target_dir, filename)
            
            # Save code
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving code: {str(e)}")
            raise
    
    def _create_readme(self, strategy_name: str, strategy_type: str, description: str, filepath: str):
        """Create a README file for the generated strategy."""
        try:
            readme_content = f"""# {strategy_name}

## Strategy Type
{strategy_type}

## Description
{description}

## Generated File
- **File**: `{os.path.basename(filepath)}`
- **Path**: `{filepath}`
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Usage
1. Review the generated code and adjust parameters as needed
2. Test the strategy in backtest mode before live trading
3. Ensure all required instruments are available in your subscription

## Notes
- This is a generated template - review and modify as needed
- Always test thoroughly before deploying to live trading
- Consider risk management and position sizing
"""
            
            readme_path = os.path.join(os.path.dirname(filepath), f"{strategy_name}_README.md")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
                
        except Exception as e:
            logger.error(f"Error creating README: {str(e)}")
    
    @log_io
    def _run(self, strategy_name: str, strategy_type: str, description: str, 
             parameters: Optional[Dict[str, Any]] = None, 
             code_content: Optional[str] = None) -> str:
        """Execute the code generation and saving."""
        try:
            # If code_content is provided, save it directly
            if code_content:
                filepath = self._save_code(code_content, strategy_name, strategy_type)
                self._create_readme(strategy_name, strategy_type, description, filepath)
                return f"Code saved successfully to: {filepath}"
            
            # Generate code based on strategy type
            generated_code = self._generate_code(strategy_name, strategy_type, description, parameters or {})
            
            # Save the generated code
            filepath = self._save_code(generated_code, strategy_name, strategy_type)
            
            # Create README
            self._create_readme(strategy_name, strategy_type, description, filepath)
            
            return f"""Strategy '{strategy_name}' generated successfully!

**File saved to**: {filepath}
**Strategy type**: {strategy_type}
**Description**: {description}

The generated code includes:
- Complete AlgoEvent class structure
- Proper callback function implementations
- Error handling and logging
- Strategy-specific logic based on type
- Documentation and comments

A README file has also been created with usage instructions.
"""
        
        except Exception as e:
            logger.error(f"Error in algogene_code_generator: {str(e)}")
            return f"Error generating code: {str(e)}"

# Create the tool instance
algogene_code_generator_tool = AlgogeneCodeGenerator()