# src/tools/algogene_client.py

import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from ..utils.logging_config import setup_logger
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
        
        # 加载instruments列表
        self.instruments_file = os.path.join(os.path.dirname(__file__), 'data', 'instruments_list.json')
        self._load_instruments()
        
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

    def _load_instruments(self):
        """加载instruments列表"""
        try:
            if os.path.exists(self.instruments_file):
                with open(self.instruments_file, 'r') as f:
                    data = json.load(f)
                    self.instruments = set(data.get('data', {}).get('res', []))
                logger.info(f"成功加载 {len(self.instruments)} 个instruments")
            else:
                logger.warning(f"Instruments文件不存在: {self.instruments_file}")
                self.instruments = set()
        except Exception as e:
            logger.error(f"加载instruments文件失败: {str(e)}")
            self.instruments = set()

    def is_valid_instrument(self, instrument: str) -> bool:
        """
        检查给定的instrument是否在支持的列表中
        
        Args:
            instrument (str): 要检查的金融工具代码
            
        Returns:
            bool: 如果instrument在支持列表中返回True，否则返回False
        """
        return instrument in self.instruments

    def get_price_history(self, count: int, instrument: str, interval: str, timestamp: str) -> Dict[str, Any]:
        """
        Get minute level historical price data(at most 90 days) from Algogene API.
        
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
                - res (Dict[str, Dict]): Dictionary of symbol data keyed by symbol name
                
                Each symbol data contains:
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
    # Historical Data APIs
    # =============================================================================
    

    def get_econs_calendar(self, start_date: Optional[str] = None, end_date: Optional[str] = None, country: Optional[str] = None) -> Dict[str, Any]:
        """
        Get historical economic calendar events.
        
        Args:
            start_date (Optional[str]): Start date in format "YYYY-MM-DD"
            end_date (Optional[str]): End date in format "YYYY-MM-DD"  
            country (Optional[str]): Country code filter
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - count (int): Number of events
                - res (List[Dict]): List of economic calendar events
                
                Each event object contains:
                    - impact (str): Impact level (e.g., "Low Impact Expected")
                    - nevent (str): Event name
                    - timestamp (str): Event timestamp in GMT+0
                    - country (str): Country code (if available)
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/history_econs_calendar"
            
            querystring = {
                "user": self.user_id,
                "api_key": self.api_key
            }
            
            if start_date:
                querystring["start_date"] = start_date
            if end_date:
                querystring["end_date"] = end_date
            if country:
                querystring["country"] = country
            
            headers = {"Content-Type": ""}
            
            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved {data.get('count', 0)} economic calendar events")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"Unexpected error in get_econs_calendar: {str(e)}")
            raise

    def get_econs_statistics(self, series_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get historical economic statistics data.
        
        Args:
            series_id (str): Economic series ID
            start_date (Optional[str]): Start date in format "YYYY-MM-DD"
            end_date (Optional[str]): End date in format "YYYY-MM-DD"
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - count (int): Number of data points
                - res (List[Dict]): List of economic data points
                - series_id (str): The series ID requested
                
                Each data point contains:
                    - date (str): Data date
                    - value (float): Statistical value
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/history_econs_stat"
            
            querystring = {
                "user": self.user_id,
                "api_key": self.api_key,
                "series_id": series_id
            }
            
            if start_date:
                querystring["start_date"] = start_date
            if end_date:
                querystring["end_date"] = end_date
            
            headers = {"Content-Type": ""}
            
            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved {data.get('count', 0)} economic statistics for series {series_id}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"Unexpected error in get_econs_statistics: {str(e)}")
            raise

    def get_historical_news(self, count: int = 10, timestamp_lt: Optional[str] = None, timestamp_gt: Optional[str] = None, 
                           language: str = "en", category: Optional[str] = None, source: Optional[str] = None) -> Dict[str, Any]:
        """
        Get historical news data.
        
        Args:
            count (int): Number of news items to return (max 100, default 10)
            timestamp_lt (Optional[str]): Get news before this timestamp ("YYYY-MM-DD HH:MM:SS")
            timestamp_gt (Optional[str]): Get news after this timestamp ("YYYY-MM-DD HH:MM:SS")
            language (str): Language code (ISO 639-1, default "en")
            category (Optional[str]): News categories, comma-separated
            source (Optional[str]): News sources, comma-separated
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - count (int): Number of news items
                - res (List[Dict]): List of news objects
                
                Each news object contains news content and metadata
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/history_news"
            
            querystring = {
                "user": self.user_id,
                "api_key": self.api_key,
                "count": min(count, 100),  # Enforce max limit
                "language": language
            }
            
            if timestamp_lt:
                querystring["timestamp_lt"] = timestamp_lt
            if timestamp_gt:
                querystring["timestamp_gt"] = timestamp_gt
            if category:
                querystring["category"] = category
            if source:
                querystring["source"] = source
            
            headers = {"Content-Type": ""}
            
            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved {data.get('count', 0)} historical news items")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"Unexpected error in get_historical_news: {str(e)}")
            raise


    def query_market_price(self, instrument: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Query historical market price data (alternative to get_price_history).
        
        Args:
            instrument (str): Financial instrument symbol
            start_date (Optional[str]): Start date in format "YYYY-MM-DD"
            end_date (Optional[str]): End date in format "YYYY-MM-DD"
        
        Returns:
            Dict[str, Any]: A dictionary containing market price data
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/query_marketprice"
            
            querystring = {
                "user": self.user_id,
                "api_key": self.api_key,
                "instrument": instrument
            }
            
            if start_date:
                querystring["start_date"] = start_date
            if end_date:
                querystring["end_date"] = end_date
            
            headers = {"Content-Type": ""}
            
            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved market price data for {instrument}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"Unexpected error in query_market_price: {str(e)}")
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

    def get_realtime_econs_stat(self) -> Dict[str, Any]:
        """
        Get the latest economic statistics data.
        
        Returns:
            Dict[str, Any]: A dictionary containing economic statistics with fields:
                - series_id (str): The series id of the economic statistics
                - title (str): The description of the economic statistics  
                - src (str): The original source of the economic statistics
                - geo (str): The applicable city/country of the economic statistics
                - tag (str): Category of the economic statistics
                - freq (str): Release frequency of the economic statistics
                - units (str): Units of the observation value
                - seasonal_adj (str): Identifier for seasonal adjustment
                - notes (str): Remarks
                - popularity (float): Popularity of the economic statistics
                - obs_date (str): Observation date of the economic statistics
                - obs_val (float): Observation value of the economic statistics
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/realtime_econs_stat"
            
            querystring = {
                "user": self.user_id,
                "api_key": self.api_key
            }
            
            headers = {"Content-Type": ""}
            
            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            
            data = response.json()
            logger.info("Successfully retrieved real-time economic statistics")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"Unexpected error in get_realtime_econs_stat: {str(e)}")
            raise

    def get_realtime_weather(self, city: str) -> Dict[str, Any]:
        """
        Get current weather information for any given city in the world.
        
        Args:
            city (str): Any city name in the world (e.g., 'Beijing', 'New York City', 'London', etc.)
        
        Returns:
            Dict[str, Any]: A dictionary containing weather information with fields:
                - timestamp (str): Latest recorded timestamp of the weather event (UTC+0)
                - city (str): City name
                - country (str): The country of the city
                - coord_lat (float): Latitude of the city's geographic coordinate
                - coord_lon (float): Longitude of the city's geographic coordinate
                - sunrise (str): Sunrise time
                - sunset (str): Estimated sunset time
                - visibility (float): Visibility in miles (None for missing value)
                - pressure (float): Atmospheric pressure in Dynes per square centimetre
                - temperature_min (float): Minimum temperature in Fahrenheit (F)
                - temperature_max (float): Maximum temperature in Fahrenheit (F)
                - temperature (float): Current temperature in Fahrenheit (F)
                - humidity (float): Humidity percentage (%)
                - wind_speed (float): Wind speed in mile per hour (mph)
                - wind_degree (float): Wind degree (0-360 degrees)
                - weather (str): High level weather classification ('Clear', 'Clouds', 'Haze', etc.)
                - weather_desc (str): Detailed weather description
                - clouds (float): Cloud density (0-100)
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/realtime_weather"
            
            querystring = {
                "user": self.user_id,
                "api_key": self.api_key,
                "city": city
            }
            
            headers = {"Content-Type": ""}
            
            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved weather data for {city}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"Unexpected error in get_realtime_weather: {str(e)}")
            raise

    def get_realtime_news(self, count: int = 10, language: str = "en", category: Optional[str] = None, source: Optional[str] = None) -> Dict[str, Any]:
        """
        Get real-time news data.
        
        Args:
            count (int): Number of news items to return (max 100, default 10)
            language (str): Language code (ISO 639-1, default "en")
            category (Optional[str]): News categories, comma-separated
            source (Optional[str]): News sources, comma-separated
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - res (Dict): Real-time news object with fields:
                    - authors (List): List of authors
                    - category (str): News category
                    - link (str): News article link
                    - movies (List): Associated media files
                    - published (str): Publication timestamp
                    - source (str): News source
                    - text (str): News article text
                    - title (str): News article title
                    - top_image (str): Featured image URL
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response contains an error
        """
        try:
            url = f"{self.base_url}/realtime_news"
            
            querystring = {
                "user": self.user_id,
                "api_key": self.api_key,
                "count": min(count, 100),  # Enforce max limit
                "lang": language  # Note: API uses 'lang' parameter name
            }
            
            if category:
                querystring["category"] = category
            if source:
                querystring["source"] = source
            
            headers = {"Content-Type": ""}
            
            response = self.session.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved {data.get('count', 0)} real-time news items")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"Unexpected error in get_realtime_news: {str(e)}")
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

def get_algogene_realtime_exchange_rate(cur1: str, cur2: str) -> Dict[str, Any]:
    """
    获取Algogene实时汇率数据的包装函数
    
    Args:
        cur1 (str): 源货币代码
        cur2 (str): 目标货币代码
        
    Returns:
        Dict[str, Any]: 实时汇率数据
    """
    try:
        client = AlgogeneClient()
        return client.get_realtime_exchange_rate(cur1, cur2)
    except Exception as e:
        logger.error(f"Algogene实时汇率数据获取失败: {e}")
        return {"error": str(e)}

def get_algogene_realtime_news(count: int = 10, language: str = "en", category: Optional[str] = None, source: Optional[str] = None) -> Dict[str, Any]:
    """
    获取Algogene实时新闻数据的包装函数
    
    Args:
        count (int): 新闻条数，默认10条
        language (str): 语言代码，默认"en"
        category (Optional[str]): 新闻分类，用逗号分隔
        source (Optional[str]): 新闻来源，用逗号分隔
        
    Returns:
        Dict[str, Any]: 实时新闻数据
    """
    try:
        client = AlgogeneClient()
        return client.get_realtime_news(count, language, category, source)
    except Exception as e:
        logger.error(f"Algogene实时新闻数据获取失败: {e}")
        return {"error": str(e)}

def get_algogene_realtime_econs_stat() -> Dict[str, Any]:
    """
    获取Algogene实时经济统计数据的包装函数
    
    Returns:
        Dict[str, Any]: 实时经济统计数据
    """
    try:
        client = AlgogeneClient()
        return client.get_realtime_econs_stat()
    except Exception as e:
        logger.error(f"Algogene实时经济统计数据获取失败: {e}")
        return {"error": str(e)}

def get_algogene_realtime_weather(city: str) -> Dict[str, Any]:
    """
    获取Algogene实时天气数据的包装函数
    
    Args:
        city (str): 城市名称
        
    Returns:
        Dict[str, Any]: 实时天气数据
    """
    try:
        client = AlgogeneClient()
        return client.get_realtime_weather(city)
    except Exception as e:
        logger.error(f"Algogene实时天气数据获取失败: {e}")
        return {"error": str(e)}

def search_instrument_with_prefix(prefix: str) -> Dict[str, Any]:
    """
    Search for instruments that start with the given prefix
    
    Args:
        prefix (str): The prefix to search for (e.g., "BTC" will find "BTCUSD", "BTCEUR", etc.)
        
    Returns:
        Dict[str, Any]: A dictionary containing:
            - matches (List[str]): List of matching instrument symbols
            - count (int): Number of matches found
            - prefix (str): The prefix that was searched for
    """
    try:
        client = AlgogeneClient()
        matches = [inst for inst in client.instruments if inst.startswith(prefix.upper())]
        result = {
            "matches": matches,
            "count": len(matches),
            "prefix": prefix.upper()
        }
        logger.info(f"Found {len(matches)} instruments matching prefix '{prefix}'")
        return result
    except Exception as e:
        logger.error(f"Instrument prefix search failed: {e}")
        return {"error": str(e)}

def check_valid_instrument(instrument: str) -> bool:
    """
    检查金融工具是否在支持的列表中
    
    Args:
        instrument (str): 要检查的金融工具代码
        
    Returns:
        bool: 如果instrument在支持列表中返回True，否则返回False
    """
    try:
        client = AlgogeneClient()
        return client.is_valid_instrument(instrument)
    except Exception as e:
        logger.error(f"检查instrument有效性失败: {e}")
        return False

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
        
        # Test get_realtime_exchange_rate
        print("\n=== Testing Real-time Exchange Rate ===")
        exchange_rate = client.get_realtime_exchange_rate("USD", "EUR")
        print("Real-time Exchange Rate Response:", json.dumps(exchange_rate, indent=2))
        
        # Test get_realtime_econs_stat
        print("\n=== Testing Real-time Economic Statistics ===")
        realtime_econs = client.get_realtime_econs_stat()
        print("Real-time Economic Statistics Response:", json.dumps(realtime_econs, indent=2))
        
        # Test get_realtime_weather
        print("\n=== Testing Real-time Weather ===")
        realtime_weather = client.get_realtime_weather("Beijing")
        print("Real-time Weather Response:", json.dumps(realtime_weather, indent=2))
        
        # Test get_realtime_news
        print("\n=== Testing Real-time News ===")
        realtime_news = client.get_realtime_news(count=5, language="en")
        print("Real-time News Response:", json.dumps(realtime_news, indent=2))
        
        
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
        print("Wrapper Realtime Price Response:", json.dumps(wrapper_realtime, indent=2))
        
        wrapper_exchange = get_algogene_realtime_exchange_rate("EUR", "USD")
        print("Wrapper Exchange Rate Response:", json.dumps(wrapper_exchange, indent=2))
        
        wrapper_news = get_algogene_realtime_news(count=3)
        print("Wrapper News Response:", json.dumps(wrapper_news, indent=2))
        
        wrapper_econs = get_algogene_realtime_econs_stat()
        print("Wrapper Economic Statistics Response:", json.dumps(wrapper_econs, indent=2))
        
        wrapper_weather = get_algogene_realtime_weather("New York City")
        print("Wrapper Weather Response:", json.dumps(wrapper_weather, indent=2))
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    main()


