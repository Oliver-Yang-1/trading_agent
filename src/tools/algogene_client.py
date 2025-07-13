# src/tools/algogene_client.py

import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from src.utils.logging_config import setup_logger
import json

logger = setup_logger('algogene_client')

class AlgogeneClient:
    """
    A client for interacting with the Algogene API.
    Handles authentication, request formatting, and response processing.
    """
    
    def __init__(self, proxy: Optional[str] = None):
        """
        Initialize the Algogene API client with authentication credentials.
        Credentials should be set in environment variables:
        - ALGOGENE_API_KEY: Your API key
        - ALGOGENE_USER_ID: Your user ID
        - ALGOGENE_PROXY: Proxy URL (optional, can also be passed as parameter)
        
        Args:
            proxy (Optional[str]): Proxy URL (e.g., 'http://127.0.0.1:7890' or 'socks5://127.0.0.1:1080')
                                 If not provided, will check ALGOGENE_PROXY environment variable
        """
        self.api_key = os.getenv('ALGOGENE_API_KEY')
        self.user_id = os.getenv('ALGOGENE_USER_ID')
        
        if not self.api_key or not self.user_id:
            raise ValueError("ALGOGENE_API_KEY and ALGOGENE_USER_ID must be set in environment variables")
            
        self.base_url = "https://algogene.com/rest/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
        # Configure proxy if provided or use system proxy
        proxy_url = proxy or os.getenv('ALGOGENE_PROXY')
        if proxy_url:
            self.session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            logger.info(f"Proxy configured: {proxy_url}")
        else:
            # Use system proxy settings if available
            self.session.trust_env = True
            logger.info("Using system proxy settings")

    def get_price_history(self, count: int, instrument: str, interval: str, timestamp: str) -> Dict[str, Any]:
        """
        Get historical price data from Algogene API.
        
        Args:
            count (int): Number of data points to retrieve
            instrument (str): Trading instrument symbol
            interval (str): Time interval for the data
            timestamp (str): Reference timestamp for the data
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - res (List[Dict]): List of candlestick data objects sorted by timestamp
                - count (int): Length of returned results
                
                Each candlestick object contains:
                
                Required fields:
                    - t (str): Timestamp at bar closing in GMT+0 (format: YYYY-MM-DD HH:MM:SS)
                    - o (float): Open price (>= 0)
                    - h (float): Highest price (>= 0)
                    - l (float): Lowest price (>= 0)
                    - c (float): Closing price (>= 0)
                    - b (float): Closing bid price (>= 0)
                    - a (float): Closing ask price (>= 0)
                    - m (float): Closing mid price (>= 0)
                    - v (int): Transaction volume (>= 1)
                    - instrument (str): Instrument name
                
                Optional fields (for FUT/OPT contracts): (not used)
                    - expiry (str): Expiry date for the instrument
                    - right (str): Option exercise right ('C' for call, 'P' for put)
                    - strike (float): Strike price for the instrument (>= 0)
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/history_price"

            querystring = {
                "user": self.user_id,
                "api_key": self.api_key,
                "count": count,
                "interval": interval,
                "timestamp": timestamp,
                "instrument": instrument
            }

            headers = {"Content-Type": ""}

            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            data = response.json()
            logger.info(f"Successfully retrieved price history for {instrument}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"Unexpected error in get_price_history: {str(e)}")
            raise
           
    def get_realtime_price(self, symbols: str, broker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get real-time market data for specified symbols.
        
        Args:
            symbols (str): A list of financial symbols separated by ',' (required)
            broker (Optional[str]): Get the realtime market data quoted by a specific broker.
                Current supported values: 'diginex', 'exness', 'ib', 'ig', 'oanda'.
                If not specified, returns the latest market data among all available brokers.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - count (int): Number of results
                - res (List[Dict]): List of real-time market data objects
                
                Each market data object contains:
                    - timestamp (str): Time in UTC+0
                    - bidPrice (float): Bid price
                    - askPrice (float): Ask price
                    - bidSize (float): Bid volume size
                    - askSize (float): Ask volume size
                    - bidOrderBook (List[float]): Bid order book
                    - askOrderBook (List[float]): Ask order book
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/realtime_price"

            querystring = {
                "user": self.user_id, 
                "api_key": self.api_key, 
                "symbols": symbols
            }

            if broker:
                querystring["broker"] = broker

            headers = {"Content-Type": ""}

            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Successfully retrieved real-time price for {symbols}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise

    # =============================================================================
    # Contract Specification APIs
    # =============================================================================
    
    def list_all_instruments(self) -> Dict[str, Any]:
        """
        Get list of all available financial instruments.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - count (int): Number of instruments
                - res (List[str]): List of instrument symbols
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/list_all_instrument"
            
            querystring = {
                "user": self.user_id,
                "api_key": self.api_key
            }
            
            headers = {"Content-Type": ""}
            
            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved {data.get('count', 0)} available instruments")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"Unexpected error in list_all_instruments: {str(e)}")
            raise

    def query_contract(self, instrument: str) -> Dict[str, Any]:
        """
        Get contract specification details for a particular financial instrument.
        
        Args:
            instrument (str): One of the financial instrument names from list_all_instrument
        
        Returns:
            Dict[str, Any]: A dictionary containing contract specification:
                - lot_size (int): Number of shares per 1 lot
                - asset_class (str): Market type ('COM', 'CRYPTO', 'ENERGY', 'EQ', 'FX', 'IR', 'METAL')
                - product_type (str): Product nature ('SPOT', 'FUT', 'OPT')
                - settlement_currency (str): Currency used for settlement
                - description (str): Description of the instrument
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/query_contract"
            
            querystring = {
                "user": self.user_id,
                "api_key": self.api_key,
                "instrument": instrument
            }
            
            headers = {"Content-Type": ""}
            
            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved contract specification for {instrument}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"Unexpected error in query_contract: {str(e)}")
            raise

    def list_econs_series(self) -> Dict[str, Any]:
        """
        Get all economic series IDs available at ALGOGENE.
        
        Returns:
            Dict[str, Any]: A dictionary containing economic series information
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/list_econs_series"
            
            querystring = {
                "user": self.user_id,
                "api_key": self.api_key
            }
            
            headers = {"Content-Type": ""}
            
            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            
            data = response.json()
            logger.info("Successfully retrieved economic series list")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"Unexpected error in list_econs_series: {str(e)}")
            raise

    def meta_econs_series(self, series_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific economic series.
        
        Args:
            series_id (str): Economic series ID
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - res (Dict): Economic series metadata including:
                    - freq (str): Frequency (e.g., "annual")
                    - geo (str): Geographic area
                    - obs_start (str): Observation start date
                    - seasonal (str): Seasonal adjustment (e.g., "NSA")
                    - series_id (str): Series ID
                    - src (str): Data source
                    - tag (str): Tags describing the data
                    - title (str): Series title
                    - units (str): Data units
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/meta_econs_series"
            
            querystring = {
                "user": self.user_id,
                "api_key": self.api_key,
                "series_id": series_id
            }
            
            headers = {"Content-Type": ""}
            
            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved metadata for economic series {series_id}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"Unexpected error in meta_econs_series: {str(e)}")
            raise

    # =============================================================================
    # Realtime Data APIs
    # =============================================================================
    
    def get_realtime_exchange_rate(self, cur1: str, cur2: str) -> Dict[str, Any]:
        """
        Get real-time exchange rate between two currencies.
        
        Args:
            cur1 (str): Exchange from currency code
            cur2 (str): Exchange to currency code
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - res (float): Exchange rate value
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/realtime_exchange_rate"
            
            querystring = {
                "user": self.user_id,
                "api_key": self.api_key,
                "cur1": cur1,
                "cur2": cur2
            }
            
            headers = {"Content-Type": ""}
            
            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved exchange rate for {cur1}/{cur2}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"Unexpected error in get_realtime_exchange_rate: {str(e)}")
            raise

# ===== 包装函数 - 供其他模块使用 =====

def get_algogene_price_history(count: int, instrument: str, interval: str, timestamp: str) -> Dict[str, Any]:
    """
    获取Algogene历史价格数据的包装函数
    
    Args:
        count (int): 数据点数量
        instrument (str): 交易工具符号
        interval (str): 时间间隔
        timestamp (str): 参考时间戳
        
    Returns:
        Dict[str, Any]: 历史价格数据
    """
    try:
        client = AlgogeneClient()
        return client.get_price_history(count, instrument, interval, timestamp)
    except Exception as e:
        logger.error(f"Algogene价格历史数据获取失败: {e}")
        return {"error": str(e)}

def get_algogene_realtime_price(symbols: str, broker: Optional[str] = None) -> Dict[str, Any]:
    """
    获取Algogene实时价格数据的包装函数
    
    Args:
        symbols (str): 金融符号列表，用逗号分隔
        broker (Optional[str]): 指定经纪商
        
    Returns:
        Dict[str, Any]: 实时价格数据
    """
    try:
        client = AlgogeneClient()
        return client.get_realtime_price(symbols, broker)
    except Exception as e:
        logger.error(f"Algogene实时价格数据获取失败: {e}")
        return {"error": str(e)}

def main():
    """
    Test function for AlgogeneClient.
    Demonstrates usage of get_price_history and get_realtime_price methods.
    """
    try:
        # Initialize the client
        client = AlgogeneClient()
        
        # Test get_price_history
        print("\n=== Testing Historical Price Data ===")
        price_history = client.get_price_history(
            count=5,
            instrument="GOOGL",
            interval="M",
            timestamp="2025-05-31 00:00:00"
        )
        print("Price History Response:", json.dumps(price_history, indent=2))
        
        # Test get_realtime_price
        print("\n=== Testing Real-time Price Data ===")
        realtime_price = client.get_realtime_price(
            symbols="BTCUSD"
        )
        print("Real-time Price Response:", json.dumps(realtime_price, indent=2))
        
        # Test wrapper functions
        print("\n=== Testing Wrapper Functions ===")
        wrapper_history = get_algogene_price_history(
            count=3,
            instrument="AAPL",
            interval="D",
            timestamp="2025-01-01 00:00:00"
        )
        print("Wrapper History Response:", json.dumps(wrapper_history, indent=2))
        
        wrapper_realtime = get_algogene_realtime_price("EURUSD")
        print("Wrapper Realtime Response:", json.dumps(wrapper_realtime, indent=2))
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    main()


