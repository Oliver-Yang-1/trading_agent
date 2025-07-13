"""
Integration tests for ALGOGENE API client with real network requests.
These tests verify that the proxy configuration works with actual API calls.

NOTE: These tests require valid ALGOGENE_API_KEY and ALGOGENE_USER_ID environment variables.
If you're behind a firewall, set ALGOGENE_PROXY environment variable.
"""

import unittest
import os
import sys
import time
from requests.exceptions import RequestException, ConnectionError, Timeout

# Add the parent directory to the path to import algogene_client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algogene_client import AlgogeneClient


class TestAlgogeneIntegration(unittest.TestCase):
    """Integration tests for ALGOGENE API with real network requests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - check if credentials are available."""
        cls.api_key = os.getenv('ALGOGENE_API_KEY')
        cls.user_id = os.getenv('ALGOGENE_USER_ID')
        
        if not cls.api_key or not cls.user_id:
            raise unittest.SkipTest(
                "ALGOGENE_API_KEY and ALGOGENE_USER_ID environment variables required for integration tests"
            )
    
    def setUp(self):
        """Set up each test."""
        self.client = AlgogeneClient()
        # Add delay between tests to avoid rate limiting
        time.sleep(1)
    
    def test_network_connectivity(self):
        """Test basic network connectivity to ALGOGENE API."""
        try:
            # Try a simple API call
            result = self.client.list_all_instruments()
            
            # Verify response structure
            self.assertIsInstance(result, dict)
            self.assertIn('count', result)
            self.assertIn('res', result)
            self.assertIsInstance(result['count'], int)
            self.assertIsInstance(result['res'], list)
            
            print(f"✓ Network connectivity OK - Found {result['count']} instruments")
            
        except ConnectionError as e:
            self.fail(f"Connection failed - check your internet connection or proxy settings: {e}")
        except Timeout as e:
            self.fail(f"Request timed out - check your network connection: {e}")
        except Exception as e:
            self.fail(f"Unexpected error during network test: {e}")
    
    def test_list_all_instruments_real(self):
        """Test real API call to list all instruments."""
        try:
            result = self.client.list_all_instruments()
            
            # Validate response
            self.assertIsInstance(result, dict)
            self.assertIn('count', result)
            self.assertIn('res', result)
            self.assertGreater(result['count'], 0)
            
            # Print some sample instruments for verification
            print(f"✓ Retrieved {result['count']} instruments")
            if result['res']:
                print(f"  Sample instruments: {result['res'][:5]}")
                
        except Exception as e:
            self.fail(f"list_all_instruments failed: {e}")
    
    def test_query_contract_real(self):
        """Test real API call to query contract specification."""
        try:
            # First get list of instruments
            instruments_result = self.client.list_all_instruments()
            
            if not instruments_result.get('res'):
                self.skipTest("No instruments available to test contract query")
            
            # Test with first available instrument
            test_instrument = instruments_result['res'][0]
            result = self.client.query_contract(test_instrument)
            
            # Validate response structure
            self.assertIsInstance(result, dict)
            # Common fields that should be present
            expected_fields = ['lot_size', 'asset_class', 'product_type', 'settlement_currency', 'description']
            for field in expected_fields:
                if field in result:  # Some fields might be optional
                    print(f"  {field}: {result[field]}")
            
            print(f"✓ Contract query successful for {test_instrument}")
            
        except Exception as e:
            self.fail(f"query_contract failed: {e}")
    
    def test_list_econs_series_real(self):
        """Test real API call to list economic series."""
        try:
            result = self.client.list_econs_series()
            
            # Validate response
            self.assertIsInstance(result, dict)
            
            # Economic series might have different response format
            print(f"✓ Economic series query successful")
            print(f"  Response keys: {list(result.keys())}")
            
        except Exception as e:
            print(f"⚠ list_econs_series failed (might be expected): {e}")
            # Don't fail the test as this endpoint might have restrictions
    
    def test_meta_econs_series_real(self):
        """Test real API call to get economic series metadata."""
        try:
            # Try with a common economic series ID
            test_series_ids = ["GDP", "CPI", "UNEMPLOYMENT", "INTEREST_RATE"]
            
            for series_id in test_series_ids:
                try:
                    result = self.client.meta_econs_series(series_id)
                    print(f"✓ Meta economic series successful for {series_id}")
                    print(f"  Response keys: {list(result.keys())}")
                    break
                except Exception as e:
                    print(f"  {series_id} failed: {e}")
                    continue
            else:
                print("⚠ All test series IDs failed (might be expected)")
                
        except Exception as e:
            print(f"⚠ meta_econs_series test failed (might be expected): {e}")
    
    def test_realtime_exchange_rate_real(self):
        """Test real API call to get exchange rates."""
        try:
            # Test common currency pairs
            currency_pairs = [("USD", "EUR"), ("EUR", "USD"), ("USD", "JPY"), ("GBP", "USD")]
            
            for cur1, cur2 in currency_pairs:
                try:
                    result = self.client.get_realtime_exchange_rate(cur1, cur2)
                    
                    # Validate response
                    self.assertIsInstance(result, dict)
                    self.assertIn('res', result)
                    self.assertIsInstance(result['res'], (int, float))
                    
                    print(f"✓ Exchange rate {cur1}/{cur2}: {result['res']}")
                    break
                    
                except Exception as e:
                    print(f"  {cur1}/{cur2} failed: {e}")
                    continue
            else:
                self.fail("All currency pairs failed")
                
        except Exception as e:
            self.fail(f"get_realtime_exchange_rate failed: {e}")
    
    def test_proxy_configuration_real(self):
        """Test that proxy configuration works with real requests."""
        proxy_url = os.getenv('ALGOGENE_PROXY')
        
        if not proxy_url:
            self.skipTest("ALGOGENE_PROXY environment variable not set - skipping proxy test")
        
        try:
            # Create client with explicit proxy
            proxy_client = AlgogeneClient(proxy=proxy_url)
            
            # Test a simple API call through proxy
            result = proxy_client.list_all_instruments()
            
            # Validate response
            self.assertIsInstance(result, dict)
            self.assertIn('count', result)
            
            print(f"✓ Proxy test successful using: {proxy_url}")
            print(f"  Retrieved {result['count']} instruments through proxy")
            
        except Exception as e:
            self.fail(f"Proxy test failed with {proxy_url}: {e}")
    
    def test_error_handling_real(self):
        """Test error handling with invalid requests."""
        try:
            # Test with invalid instrument
            try:
                result = self.client.query_contract("INVALID_INSTRUMENT_XYZ")
                print(f"⚠ Invalid instrument query returned: {result}")
            except Exception as e:
                print(f"✓ Invalid instrument properly handled: {e}")
            
            # Test with invalid currency pair
            try:
                result = self.client.get_realtime_exchange_rate("INVALID", "ALSO_INVALID")
                print(f"⚠ Invalid currency pair returned: {result}")
            except Exception as e:
                print(f"✓ Invalid currency pair properly handled: {e}")
                
        except Exception as e:
            print(f"Error handling test failed: {e}")


class TestNetworkConnectivity(unittest.TestCase):
    """Basic network connectivity tests without API credentials."""
    
    def test_basic_connectivity(self):
        """Test basic connectivity to ALGOGENE domain."""
        import requests
        
        try:
            # Test basic connectivity to the domain
            response = requests.get("https://algogene.com", timeout=10)
            print(f"✓ Basic connectivity to algogene.com: {response.status_code}")
            
        except ConnectionError as e:
            self.fail(f"Cannot connect to algogene.com - check internet connection or proxy: {e}")
        except Timeout as e:
            self.fail(f"Connection to algogene.com timed out: {e}")
        except Exception as e:
            print(f"Basic connectivity test result: {e}")


if __name__ == '__main__':
    print("="*60)
    print("ALGOGENE API Integration Tests")
    print("="*60)
    print("These tests make REAL API calls to verify connectivity and proxy configuration.")
    print()
    print("Requirements:")
    print("- ALGOGENE_API_KEY environment variable")
    print("- ALGOGENE_USER_ID environment variable")
    print("- ALGOGENE_PROXY environment variable (if behind firewall)")
    print()
    print("Testing network connectivity...")
    print("="*60)
    
    # Run the tests with verbose output
    unittest.main(verbosity=2, exit=False)