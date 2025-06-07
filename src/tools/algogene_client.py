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
    
    def __init__(self):
        """
        Initialize the Algogene API client with authentication credentials.
        Credentials should be set in environment variables:
        - ALGOGENE_API_KEY: Your API key
        - ALGOGENE_USER_ID: Your user ID
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

            response = requests.request("GET", url, headers=headers, params=querystring)
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

            response = requests.request("GET", url, headers=headers, params=querystring)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Successfully retrieved real-time price for {symbols}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise

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
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    main()


