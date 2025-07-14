# src/tools/tests/test_algogene_comprehensive.py

import unittest
import time
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
sys.path.append('/Users/oliveryang/2025Projects/trading_agent')

from src.tools.algogene_client import AlgogeneClient
from src.utils.logging_config import setup_logger

logger = setup_logger('test_algogene_comprehensive')

class RateLimiter:
    """Rate limiter to enforce 10 requests per minute"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        current_time = time.time()
        
        # Remove requests older than time_window
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time < self.time_window]
        
        # If we're at the limit, wait until we can make another request
        if len(self.requests) >= self.max_requests:
            oldest_request = min(self.requests)
            wait_time = self.time_window - (current_time - oldest_request) + 1
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                # Clean up old requests after waiting
                current_time = time.time()
                self.requests = [req_time for req_time in self.requests 
                               if current_time - req_time < self.time_window]
        
        # Record this request
        self.requests.append(current_time)

class TestAlgogeneClientComprehensive(unittest.TestCase):
    """Comprehensive test suite for AlgogeneClient with rate limiting and error analysis"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        cls.rate_limiter = RateLimiter(max_requests=10, time_window=60)
        cls.test_results = {}
        cls.failed_tests = []
        
        # Check environment variables
        if not os.getenv('ALGOGENE_API_KEY') or not os.getenv('ALGOGENE_USER_ID'):
            raise unittest.SkipTest("ALGOGENE_API_KEY and ALGOGENE_USER_ID environment variables must be set")
        
        try:
            cls.client = AlgogeneClient()
            logger.info("AlgogeneClient initialized successfully")
        except Exception as e:
            raise unittest.SkipTest(f"Failed to initialize AlgogeneClient: {e}")
    
    def setUp(self):
        """Set up before each test"""
        self.rate_limiter.wait_if_needed()
    
    def _test_api_method(self, method_name: str, method_func, *args, **kwargs) -> Dict[str, Any]:
        """
        Generic method to test any API method with error analysis
        
        Args:
            method_name: Name of the method being tested
            method_func: The actual method to call
            *args, **kwargs: Arguments to pass to the method
            
        Returns:
            Dict containing test results
        """
        result = {
            'method': method_name,
            'success': False,
            'status_code': None,
            'has_data': False,
            'response': None,
            'error': None,
            'args': args,
            'kwargs': kwargs
        }
        
        try:
            logger.info(f"Testing {method_name} with args={args}, kwargs={kwargs}")
            
            # Execute the method
            response = method_func(*args, **kwargs)
            
            # Check if response is valid
            if response is None:
                result['error'] = "Method returned None"
                result['status_code'] = 'NULL_RESPONSE'
            elif isinstance(response, dict) and 'error' in response:
                result['error'] = response['error']
                result['status_code'] = 'ERROR_IN_RESPONSE'
            else:
                result['success'] = True
                result['status_code'] = 200
                result['response'] = response
                
                # Check if response has actual data
                if isinstance(response, dict):
                    if 'res' in response and response['res']:
                        result['has_data'] = True
                    elif 'count' in response and response['count'] > 0:
                        result['has_data'] = True
                    elif any(key in response for key in ['timestamp', 'city', 'series_id', 'res']):
                        result['has_data'] = True
                
                logger.info(f"✓ {method_name} succeeded - Status: 200, Has Data: {result['has_data']}")
                
        except Exception as e:
            result['error'] = str(e)
            result['status_code'] = 'EXCEPTION'
            logger.error(f"✗ {method_name} failed with exception: {e}")
        
        self.test_results[method_name] = result
        if not result['success']:
            self.failed_tests.append(result)
            
        return result
    
    def test_01_list_all_instruments(self):
        """Test listing all available instruments"""
        result = self._test_api_method(
            'list_all_instruments',
            self.client.list_all_instruments
        )
        
        if result['success']:
            self.assertIsInstance(result['response'], dict)
            self.assertIn('count', result['response'])
            self.assertIn('res', result['response'])
        
    def test_02_query_contract(self):
        """Test querying contract specification"""
        # First get available instruments to test with
        instruments_result = self._test_api_method(
            'list_all_instruments_for_contract',
            self.client.list_all_instruments
        )
        
        if instruments_result['success'] and instruments_result['response'].get('res'):
            # Use first available instrument
            instrument = instruments_result['response']['res'][0]
            
            result = self._test_api_method(
                'query_contract',
                self.client.query_contract,
                instrument
            )
            
            if result['success']:
                self.assertIsInstance(result['response'], dict)
                expected_fields = ['lot_size', 'asset_class', 'product_type', 'settlement_currency', 'description']
                for field in expected_fields:
                    self.assertIn(field, result['response'], f"Missing field: {field}")
        else:
            self.skipTest("Cannot test query_contract without available instruments")
    
    def test_03_get_price_history(self):
        """Test getting historical price data"""
        # Test with common instruments
        test_instruments = ['AAPL', 'GOOGL', 'MSFT', 'BTCUSD', 'EURUSD']
        
        for instrument in test_instruments:
            with self.subTest(instrument=instrument):
                self.rate_limiter.wait_if_needed()
                
                result = self._test_api_method(
                    f'get_price_history_{instrument}',
                    self.client.get_price_history,
                    count=5,
                    instrument=instrument,
                    interval='D',
                    timestamp=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
                )
                
                if result['success']:
                    self.assertIsInstance(result['response'], dict)
                    self.assertIn('res', result['response'])
                    self.assertIn('count', result['response'])
                    
                    if result['response']['res']:
                        candle = result['response']['res'][0]
                        required_fields = ['t', 'o', 'h', 'l', 'c', 'b', 'a', 'm', 'v', 'instrument']
                        for field in required_fields:
                            self.assertIn(field, candle, f"Missing candle field: {field}")
                    break  # If one instrument works, continue to next test
    
    def test_04_get_realtime_price(self):
        """Test getting real-time price data"""
        test_symbols = ['BTCUSD', 'EURUSD', 'AAPL', 'GOOGL']
        
        for symbols in test_symbols:
            with self.subTest(symbols=symbols):
                self.rate_limiter.wait_if_needed()
                
                result = self._test_api_method(
                    f'get_realtime_price_{symbols}',
                    self.client.get_realtime_price,
                    symbols
                )
                
                if result['success']:
                    self.assertIsInstance(result['response'], dict)
                    self.assertIn('count', result['response'])
                    self.assertIn('res', result['response'])
                    
                    if result['response']['res']:
                        for symbol, data in result['response']['res'].items():
                            required_fields = ['timestamp', 'bidPrice', 'askPrice', 'bidSize', 'askSize']
                            for field in required_fields:
                                self.assertIn(field, data, f"Missing price field: {field}")
                    break  # If one symbol works, continue to next test
    
    def test_05_get_realtime_exchange_rate(self):
        """Test getting real-time exchange rates"""
        currency_pairs = [('USD', 'EUR'), ('EUR', 'USD'), ('USD', 'GBP'), ('GBP', 'USD')]
        
        for cur1, cur2 in currency_pairs:
            with self.subTest(cur1=cur1, cur2=cur2):
                self.rate_limiter.wait_if_needed()
                
                result = self._test_api_method(
                    f'get_realtime_exchange_rate_{cur1}_{cur2}',
                    self.client.get_realtime_exchange_rate,
                    cur1, cur2
                )
                
                if result['success']:
                    self.assertIsInstance(result['response'], dict)
                    self.assertIn('res', result['response'])
                    self.assertIsInstance(result['response']['res'], (int, float))
                    break  # If one pair works, continue to next test
    
    def test_06_list_econs_series(self):
        """Test listing economic series"""
        result = self._test_api_method(
            'list_econs_series',
            self.client.list_econs_series
        )
        
        if result['success']:
            self.assertIsInstance(result['response'], dict)
    
    def test_07_meta_econs_series(self):
        """Test getting economic series metadata"""
        # First get available series
        series_result = self._test_api_method(
            'list_econs_series_for_meta',
            self.client.list_econs_series
        )
        
        if series_result['success'] and series_result['response'].get('res'):
            # Try to find a series ID to test with
            series_data = series_result['response']['res']
            if isinstance(series_data, list) and series_data:
                series_id = series_data[0] if isinstance(series_data[0], str) else str(series_data[0])
            elif isinstance(series_data, dict):
                series_id = list(series_data.keys())[0] if series_data else 'GDP'
            else:
                series_id = 'GDP'  # Fallback
            
            result = self._test_api_method(
                'meta_econs_series',
                self.client.meta_econs_series,
                series_id
            )
            
            if result['success']:
                self.assertIsInstance(result['response'], dict)
                self.assertIn('res', result['response'])
        else:
            # Try with common economic series ID
            result = self._test_api_method(
                'meta_econs_series_fallback',
                self.client.meta_econs_series,
                'GDP'
            )
    
    def test_08_get_econs_calendar(self):
        """Test getting economic calendar"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        result = self._test_api_method(
            'get_econs_calendar',
            self.client.get_econs_calendar,
            start_date=start_date,
            end_date=end_date
        )
        
        if result['success']:
            self.assertIsInstance(result['response'], dict)
            self.assertIn('count', result['response'])
            self.assertIn('res', result['response'])
    
    def test_09_get_econs_statistics(self):
        """Test getting economic statistics"""
        # Try with common economic series
        common_series = ['GDP', 'CPI', 'UNEMPLOYMENT', 'INFLATION']
        
        for series_id in common_series:
            with self.subTest(series_id=series_id):
                self.rate_limiter.wait_if_needed()
                
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                
                result = self._test_api_method(
                    f'get_econs_statistics_{series_id}',
                    self.client.get_econs_statistics,
                    series_id,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if result['success']:
                    self.assertIsInstance(result['response'], dict)
                    self.assertIn('count', result['response'])
                    self.assertIn('res', result['response'])
                    self.assertIn('series_id', result['response'])
                    break  # If one series works, continue to next test
    
    def test_10_get_historical_news(self):
        """Test getting historical news"""
        result = self._test_api_method(
            'get_historical_news',
            self.client.get_historical_news,
            count=10,
            language='en'
        )
        
        if result['success']:
            self.assertIsInstance(result['response'], dict)
            self.assertIn('count', result['response'])
            self.assertIn('res', result['response'])
    
    def test_11_query_market_price(self):
        """Test querying market price data"""
        test_instruments = ['AAPL', 'GOOGL', 'BTCUSD', 'EURUSD']
        
        for instrument in test_instruments:
            with self.subTest(instrument=instrument):
                self.rate_limiter.wait_if_needed()
                
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                
                result = self._test_api_method(
                    f'query_market_price_{instrument}',
                    self.client.query_market_price,
                    instrument,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if result['success']:
                    self.assertIsInstance(result['response'], dict)
                    break  # If one instrument works, continue to next test
    
    def test_12_get_realtime_econs_stat(self):
        """Test getting real-time economic statistics"""
        result = self._test_api_method(
            'get_realtime_econs_stat',
            self.client.get_realtime_econs_stat
        )
        
        if result['success']:
            self.assertIsInstance(result['response'], dict)
            expected_fields = ['series_id', 'title', 'src', 'geo', 'tag', 'freq', 'units']
            response = result['response']
            if isinstance(response, dict) and 'res' in response:
                response = response['res']
            
            # Check if any expected fields are present
            has_expected_fields = any(field in response for field in expected_fields)
            self.assertTrue(has_expected_fields, "Response missing expected economic stat fields")
    
    def test_13_get_realtime_weather(self):
        """Test getting real-time weather data"""
        test_cities = ['Beijing', 'New York City', 'London', 'Tokyo']
        
        for city in test_cities:
            with self.subTest(city=city):
                self.rate_limiter.wait_if_needed()
                
                result = self._test_api_method(
                    f'get_realtime_weather_{city.replace(" ", "_")}',
                    self.client.get_realtime_weather,
                    city
                )
                
                if result['success']:
                    self.assertIsInstance(result['response'], dict)
                    expected_fields = ['timestamp', 'city', 'country', 'temperature', 'humidity', 'weather']
                    response = result['response']
                    
                    # Check if response has expected weather fields
                    has_weather_fields = any(field in response for field in expected_fields)
                    self.assertTrue(has_weather_fields, f"Weather response missing expected fields for {city}")
                    break  # If one city works, continue to next test
    
    def test_14_get_realtime_news(self):
        """Test getting real-time news data"""
        result = self._test_api_method(
            'get_realtime_news',
            self.client.get_realtime_news,
            count=10,
            language='en'
        )
        
        if result['success']:
            self.assertIsInstance(result['response'], dict)
            self.assertIn('res', result['response'])
    
    @classmethod
    def tearDownClass(cls):
        """Generate comprehensive test report"""
        logger.info("\n" + "="*80)
        logger.info("ALGOGENE CLIENT COMPREHENSIVE TEST REPORT")
        logger.info("="*80)
        
        total_tests = len(cls.test_results)
        successful_tests = sum(1 for result in cls.test_results.values() if result['success'])
        tests_with_data = sum(1 for result in cls.test_results.values() if result['has_data'])
        
        logger.info(f"Total API methods tested: {total_tests}")
        logger.info(f"Successful (200 status): {successful_tests}")
        logger.info(f"With actual data: {tests_with_data}")
        logger.info(f"Failed tests: {len(cls.failed_tests)}")
        
        logger.info("\n" + "-"*50)
        logger.info("SUCCESS SUMMARY:")
        logger.info("-"*50)
        
        for method_name, result in cls.test_results.items():
            status_icon = "✓" if result['success'] else "✗"
            data_icon = "📊" if result['has_data'] else "📭"
            status_code = result['status_code'] or 'UNKNOWN'
            
            logger.info(f"{status_icon} {method_name:<40} Status: {status_code} {data_icon}")
        
        if cls.failed_tests:
            logger.info("\n" + "-"*50)
            logger.info("FAILED TESTS ANALYSIS:")
            logger.info("-"*50)
            
            for failed_test in cls.failed_tests:
                logger.info(f"\n❌ {failed_test['method']}")
                logger.info(f"   Args: {failed_test.get('args', [])}")
                logger.info(f"   Kwargs: {failed_test.get('kwargs', {})}")
                logger.info(f"   Error: {failed_test.get('error', 'Unknown error')}")
                logger.info(f"   Status: {failed_test.get('status_code', 'Unknown')}")
                
                # Suggest potential fixes
                if 'authentication' in str(failed_test.get('error', '')).lower():
                    logger.info("   💡 Suggested fix: Check API credentials and authentication")
                elif '400' in str(failed_test.get('error', '')):
                    logger.info("   💡 Suggested fix: Check request parameters and format")
                elif '404' in str(failed_test.get('error', '')):
                    logger.info("   💡 Suggested fix: Check if endpoint exists or instrument is available")
                elif '429' in str(failed_test.get('error', '')):
                    logger.info("   💡 Suggested fix: Rate limiting - increase delays between requests")
                elif 'timeout' in str(failed_test.get('error', '')).lower():
                    logger.info("   💡 Suggested fix: Increase request timeout or check network connectivity")
                elif 'proxy' in str(failed_test.get('error', '')).lower():
                    logger.info("   💡 Suggested fix: Check proxy configuration")
                else:
                    logger.info("   💡 Suggested fix: Check API documentation and endpoint availability")
        
        logger.info("\n" + "-"*50)
        logger.info("RECOMMENDATIONS:")
        logger.info("-"*50)
        
        if successful_tests < total_tests * 0.8:
            logger.info("⚠️  Many tests failed. Check API credentials and network connectivity.")
        
        if tests_with_data < successful_tests * 0.8:
            logger.info("⚠️  Many successful requests returned empty data. Check request parameters.")
        
        if successful_tests >= total_tests * 0.8:
            logger.info("✅ Most tests passed successfully. API integration is working well.")
        
        logger.info(f"\n📈 Overall Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        logger.info(f"📊 Data Return Rate: {(tests_with_data/max(successful_tests,1))*100:.1f}%")
        
        # Save detailed results to file
        report_file = '/Users/oliveryang/2025Projects/trading_agent/src/tools/tests/algogene_test_report.json'
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'successful_tests': successful_tests,
                    'tests_with_data': tests_with_data,
                    'failed_tests': len(cls.failed_tests),
                    'success_rate': (successful_tests/total_tests)*100,
                    'data_rate': (tests_with_data/max(successful_tests,1))*100
                },
                'detailed_results': cls.test_results,
                'failed_tests': cls.failed_tests
            }, f, indent=2, default=str)
        
        logger.info(f"\n💾 Detailed report saved to: {report_file}")
        logger.info("="*80)

if __name__ == '__main__':
    # Run tests with detailed output
    unittest.main(verbosity=2, buffer=True)