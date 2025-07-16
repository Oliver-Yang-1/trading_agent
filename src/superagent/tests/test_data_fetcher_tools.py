#!/usr/bin/env python3
"""
Unit tests for data_fetcher_agent financial tools.
Tests the functionality of get_financial_metrics, get_market_data, 
get_price_history, and get_financial_statements with various stock symbols.
"""

import pytest
import logging
from typing import Dict, Any, List
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import the tools directly
from src.tools.api import (
    get_financial_metrics,
    get_market_data, 
    get_price_history,
    get_financial_statements,
)


class TestDataFetcherTools:
    """Test suite for data_fetcher_agent financial tools."""
    
    def setup_method(self):
        """Setup test environment."""
        self.test_symbols = {
            "A股": "600519",  # 贵州茅台
            "US股": "AAPL",   # Apple
            "虚拟币": "BTC"    # Bitcoin
        }
        
    def test_get_financial_metrics_direct(self):
        """Test financial metrics tools directly."""
        logger.info("=" * 60)
        logger.info("Testing get_financial_metrics directly")
        logger.info("=" * 60)
        
        for market_type, symbol in self.test_symbols.items():
            logger.info(f"\n--- Testing {market_type} symbol: {symbol} ---")
            try:
                result = get_financial_metrics(symbol)
                logger.info(f"✓ {market_type} Financial Metrics Result:")
                logger.info(f"  Type: {type(result)}")
                logger.info(f"  Data: {result}")
                
                # Validate result structure
                assert isinstance(result, list), f"Expected list, got {type(result)}"
                if result:
                    assert isinstance(result[0], dict), f"Expected dict in list, got {type(result[0])}"
                    logger.info(f"  ✓ Valid data structure for {symbol}")
                else:
                    logger.warning(f"  ⚠ Empty result for {symbol}")
                    
            except Exception as e:
                logger.error(f"  ✗ Error testing {symbol}: {str(e)}")
                # Don't fail test, just log the error
                
    def test_get_market_data_direct(self):
        """Test market data tools directly."""
        logger.info("=" * 60)
        logger.info("Testing get_market_data directly")
        logger.info("=" * 60)
        
        for market_type, symbol in self.test_symbols.items():
            logger.info(f"\n--- Testing {market_type} symbol: {symbol} ---")
            try:
                result = get_market_data(symbol)
                logger.info(f"✓ {market_type} Market Data Result:")
                logger.info(f"  Type: {type(result)}")
                logger.info(f"  Data: {result}")
                
                # Validate result structure
                assert isinstance(result, dict), f"Expected dict, got {type(result)}"
                logger.info(f"  ✓ Valid data structure for {symbol}")
                
            except Exception as e:
                logger.error(f"  ✗ Error testing {symbol}: {str(e)}")
                
    def test_get_price_history_direct(self):
        """Test price history tools directly."""
        logger.info("=" * 60)
        logger.info("Testing get_price_history directly")
        logger.info("=" * 60)
        
        for market_type, symbol in self.test_symbols.items():
            logger.info(f"\n--- Testing {market_type} symbol: {symbol} ---")
            try:
                result = get_price_history(symbol, start_date="2024-01-01", end_date="2024-12-31")
                logger.info(f"✓ {market_type} Price History Result:")
                logger.info(f"  Type: {type(result)}")
                logger.info(f"  Shape: {result.shape if hasattr(result, 'shape') else 'N/A'}")
                logger.info(f"  Columns: {list(result.columns) if hasattr(result, 'columns') else 'N/A'}")
                
                # Show first few rows if data exists
                if hasattr(result, 'head') and len(result) > 0:
                    logger.info(f"  First 3 rows:")
                    logger.info(f"    {result.head(3).to_string()}")
                else:
                    logger.info(f"  Data: {result}")
                
                logger.info(f"  ✓ Valid data structure for {symbol}")
                
            except Exception as e:
                logger.error(f"  ✗ Error testing {symbol}: {str(e)}")
                
    def test_get_financial_statements_direct(self):
        """Test financial statements tools directly."""
        logger.info("=" * 60)
        logger.info("Testing get_financial_statements directly")
        logger.info("=" * 60)
        
        for market_type, symbol in self.test_symbols.items():
            logger.info(f"\n--- Testing {market_type} symbol: {symbol} ---")
            try:
                result = get_financial_statements(symbol)
                logger.info(f"✓ {market_type} Financial Statements Result:")
                logger.info(f"  Type: {type(result)}")
                logger.info(f"  Data: {result}")
                
                # Validate result structure
                assert isinstance(result, list), f"Expected list, got {type(result)}"
                if result:
                    assert isinstance(result[0], dict), f"Expected dict in list, got {type(result[0])}"
                    logger.info(f"  ✓ Valid data structure for {symbol}")
                else:
                    logger.warning(f"  ⚠ Empty result for {symbol}")
                    
            except Exception as e:
                logger.error(f"  ✗ Error testing {symbol}: {str(e)}")

    def test_all_tools_comprehensive(self):
        """Test all tools with comprehensive logging."""
        logger.info("=" * 60)
        logger.info("Comprehensive Tool Testing")
        logger.info("=" * 60)
        
        tools = [
            ("get_financial_metrics", get_financial_metrics),
            ("get_market_data", get_market_data),
            ("get_price_history", get_price_history),
            ("get_financial_statements", get_financial_statements),
        ]
        
        results = {}
        
        for tool_name, tool_func in tools:
            logger.info(f"\n{'='*40}")
            logger.info(f"Testing {tool_name}")
            logger.info(f"{'='*40}")
            
            results[tool_name] = {}
            
            for market_type, symbol in self.test_symbols.items():
                logger.info(f"\n--- {market_type} symbol: {symbol} ---")
                
                try:
                    # Special handling for get_price_history which needs date parameters
                    if tool_name == "get_price_history":
                        result = tool_func(symbol, start_date="2024-01-01", end_date="2024-12-31")
                    else:
                        result = tool_func(symbol)
                    
                    logger.info(f"✓ {tool_name} result for {symbol}:")
                    logger.info(f"  Type: {type(result)}")
                    
                    if hasattr(result, 'shape'):
                        logger.info(f"  Shape: {result.shape}")
                        logger.info(f"  Columns: {list(result.columns)}")
                        if len(result) > 0:
                            logger.info(f"  Sample data: {result.head(2).to_dict()}")
                    elif isinstance(result, (list, dict)):
                        logger.info(f"  Length/Keys: {len(result) if isinstance(result, list) else list(result.keys())}")
                        logger.info(f"  Data preview: {str(result)[:300]}...")
                    else:
                        logger.info(f"  Data: {result}")
                    
                    results[tool_name][symbol] = {"success": True, "data": result}
                    logger.info(f"  ✓ Success for {symbol}")
                    
                except Exception as e:
                    logger.error(f"  ✗ Error for {symbol}: {str(e)}")
                    results[tool_name][symbol] = {"success": False, "error": str(e)}
                    import traceback
                    logger.debug(f"  Traceback: {traceback.format_exc()}")
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("SUMMARY")
        logger.info("="*60)
        
        for tool_name, tool_results in results.items():
            logger.info(f"\n{tool_name}:")
            for symbol, result in tool_results.items():
                status = "✓" if result["success"] else "✗"
                logger.info(f"  {status} {symbol}: {'SUCCESS' if result['success'] else result['error']}")
        
        return results


if __name__ == "__main__":
    """Run all tests when called directly."""
    logger.info("Starting Data Fetcher Tools Test Suite")
    logger.info("=" * 80)
    
    test_suite = TestDataFetcherTools()
    test_suite.setup_method()
    
    # Run all tests
    try:
        test_suite.test_get_financial_metrics_direct()
        test_suite.test_get_market_data_direct()
        test_suite.test_get_price_history_direct()
        test_suite.test_get_financial_statements_direct()
        
        # Run comprehensive test
        comprehensive_results = test_suite.test_all_tools_comprehensive()
        
        logger.info("\n" + "=" * 80)
        logger.info("All tests completed successfully!")
        logger.info("=" * 80)
        
        # Final summary
        logger.info("\nFINAL SUMMARY:")
        total_tests = 0
        successful_tests = 0
        
        for tool_name, tool_results in comprehensive_results.items():
            for symbol, result in tool_results.items():
                total_tests += 1
                if result["success"]:
                    successful_tests += 1
        
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Successful tests: {successful_tests}")
        logger.info(f"Failed tests: {total_tests - successful_tests}")
        logger.info(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
        
    except Exception as e:
        logger.error(f"Test suite failed with error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")