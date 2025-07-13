"""
Test cases for ALGOGENE Contract Specification APIs.
Tests the contract specification functionality of AlgogeneClient.
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the path to import algogene_client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algogene_client import AlgogeneClient


class TestContractSpecification(unittest.TestCase):
    """Test cases for Contract Specification APIs."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.test_api_key = "test_api_key_12345"
        self.test_user_id = "test_user_id_67890"
        
        # Patch environment variables
        self.env_patcher = patch.dict(os.environ, {
            'ALGOGENE_API_KEY': self.test_api_key,
            'ALGOGENE_USER_ID': self.test_user_id
        })
        self.env_patcher.start()
        
        # Mock session to avoid actual HTTP requests
        self.session_mock = Mock()
        self.response_mock = Mock()
        self.session_mock.request.return_value = self.response_mock
        self.response_mock.raise_for_status.return_value = None
        
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    @patch('algogene_client.requests.Session')
    def test_list_all_instruments_success(self, mock_session_class):
        """Test successful retrieval of all instruments."""
        # Setup mock
        mock_session_class.return_value = self.session_mock
        mock_response_data = {
            "count": 3,
            "res": ["AAPL", "GOOGL", "MSFT"]
        }
        self.response_mock.json.return_value = mock_response_data
        
        # Create client and test
        client = AlgogeneClient()
        result = client.list_all_instruments()
        
        # Assertions
        self.assertEqual(result, mock_response_data)
        self.session_mock.request.assert_called_once_with(
            "GET",
            "https://algogene.com/rest/v1/list_all_instrument",
            headers={"Content-Type": ""},
            params={
                "user": self.test_user_id,
                "api_key": self.test_api_key
            }
        )
    
    @patch('algogene_client.requests.Session')
    def test_query_contract_success(self, mock_session_class):
        """Test successful contract specification query."""
        # Setup mock
        mock_session_class.return_value = self.session_mock
        mock_response_data = {
            "lot_size": 100,
            "asset_class": "EQ",
            "product_type": "SPOT",
            "settlement_currency": "USD",
            "description": "Apple Inc. Common Stock"
        }
        self.response_mock.json.return_value = mock_response_data
        
        # Create client and test
        client = AlgogeneClient()
        result = client.query_contract("AAPL")
        
        # Assertions
        self.assertEqual(result, mock_response_data)
        self.session_mock.request.assert_called_once_with(
            "GET",
            "https://algogene.com/rest/v1/query_contract",
            headers={"Content-Type": ""},
            params={
                "user": self.test_user_id,
                "api_key": self.test_api_key,
                "instrument": "AAPL"
            }
        )
    
    @patch('algogene_client.requests.Session')
    def test_list_econs_series_success(self, mock_session_class):
        """Test successful economic series listing."""
        # Setup mock
        mock_session_class.return_value = self.session_mock
        mock_response_data = {
            "count": 2,
            "res": ["GDP_US", "CPI_US"]
        }
        self.response_mock.json.return_value = mock_response_data
        
        # Create client and test
        client = AlgogeneClient()
        result = client.list_econs_series()
        
        # Assertions
        self.assertEqual(result, mock_response_data)
        self.session_mock.request.assert_called_once_with(
            "GET",
            "https://algogene.com/rest/v1/list_econs_series",
            headers={"Content-Type": ""},
            params={
                "user": self.test_user_id,
                "api_key": self.test_api_key
            }
        )
    
    @patch('algogene_client.requests.Session')
    def test_meta_econs_series_success(self, mock_session_class):
        """Test successful economic series metadata retrieval."""
        # Setup mock
        mock_session_class.return_value = self.session_mock
        mock_response_data = {
            "res": {
                "freq": "annual",
                "geo": "US",
                "obs_start": "1947-01-01",
                "seasonal": "NSA",
                "series_id": "GDP_US",
                "src": "BEA",
                "tag": "gdp,economic,growth",
                "title": "Gross Domestic Product",
                "units": "Billions of Dollars"
            }
        }
        self.response_mock.json.return_value = mock_response_data
        
        # Create client and test
        client = AlgogeneClient()
        result = client.meta_econs_series("GDP_US")
        
        # Assertions
        self.assertEqual(result, mock_response_data)
        self.session_mock.request.assert_called_once_with(
            "GET",
            "https://algogene.com/rest/v1/meta_econs_series",
            headers={"Content-Type": ""},
            params={
                "user": self.test_user_id,
                "api_key": self.test_api_key,
                "series_id": "GDP_US"
            }
        )
    
    @patch('algogene_client.requests.Session')
    def test_get_realtime_exchange_rate_success(self, mock_session_class):
        """Test successful real-time exchange rate retrieval."""
        # Setup mock
        mock_session_class.return_value = self.session_mock
        mock_response_data = {
            "res": 1.0823
        }
        self.response_mock.json.return_value = mock_response_data
        
        # Create client and test
        client = AlgogeneClient()
        result = client.get_realtime_exchange_rate("EUR", "USD")
        
        # Assertions
        self.assertEqual(result, mock_response_data)
        self.session_mock.request.assert_called_once_with(
            "GET",
            "https://algogene.com/rest/v1/realtime_exchange_rate",
            headers={"Content-Type": ""},
            params={
                "user": self.test_user_id,
                "api_key": self.test_api_key,
                "cur1": "EUR",
                "cur2": "USD"
            }
        )
    
    @patch('algogene_client.requests.Session')
    def test_proxy_configuration(self, mock_session_class):
        """Test proxy configuration in client initialization."""
        # Setup mock
        mock_session_instance = Mock()
        mock_session_class.return_value = mock_session_instance
        
        # Test with explicit proxy
        proxy_url = "http://127.0.0.1:7890"
        client = AlgogeneClient(proxy=proxy_url)
        
        # Verify proxy was set
        expected_proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        self.assertEqual(mock_session_instance.proxies, expected_proxies)
    
    @patch('algogene_client.requests.Session')
    def test_system_proxy_configuration(self, mock_session_class):
        """Test system proxy configuration."""
        # Setup mock
        mock_session_instance = Mock()
        mock_session_class.return_value = mock_session_instance
        
        # Test without explicit proxy (should use system proxy)
        client = AlgogeneClient()
        
        # Verify trust_env was set for system proxy
        self.assertTrue(mock_session_instance.trust_env)
    
    def test_missing_credentials(self):
        """Test error handling when credentials are missing."""
        # Remove environment variables
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                AlgogeneClient()
            
            self.assertIn("ALGOGENE_API_KEY and ALGOGENE_USER_ID must be set", str(context.exception))
    
    @patch('algogene_client.requests.Session')
    def test_api_request_failure(self, mock_session_class):
        """Test handling of API request failures."""
        # Setup mock to raise exception
        mock_session_class.return_value = self.session_mock
        self.response_mock.raise_for_status.side_effect = Exception("Connection error")
        
        # Create client and test
        client = AlgogeneClient()
        with self.assertRaises(Exception) as context:
            client.list_all_instruments()
        
        self.assertIn("Connection error", str(context.exception))
    
    @patch('algogene_client.requests.Session')
    def test_json_decode_error(self, mock_session_class):
        """Test handling of JSON decode errors."""
        # Setup mock to return invalid JSON
        import json
        mock_session_class.return_value = self.session_mock
        self.response_mock.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        # Create client and test
        client = AlgogeneClient()
        with self.assertRaises(ValueError) as context:
            client.list_all_instruments()
        
        self.assertIn("Invalid JSON response from API", str(context.exception))


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)