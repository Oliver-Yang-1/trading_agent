#!/usr/bin/env python3
"""
Test script to showcase the enhanced docstrings for financial data tools.
This demonstrates the comprehensive documentation added to the financial tools.
"""

def showcase_enhanced_docstrings():
    """展示增强的文档字符串"""
    from src.tools.api import (
        get_financial_metrics,
        get_market_data,
        get_financial_statements,
        get_price_history
    )
    
    print("=" * 80)
    print("ENHANCED FINANCIAL TOOLS DOCUMENTATION")
    print("=" * 80)
    
    financial_tools = [
        ("get_financial_metrics", get_financial_metrics),
        ("get_market_data", get_market_data),
        ("get_financial_statements", get_financial_statements),
        ("get_price_history", get_price_history),
    ]
    
    for tool_name, tool_func in financial_tools:
        print(f"\n{'='*20} {tool_name.upper()} {'='*20}")
        print(f"Function: {tool_func.__name__}")
        
        # Get function signature
        import inspect
        sig = inspect.signature(tool_func)
        print(f"Signature: {sig}")
        
        # Print docstring
        docstring = tool_func.__doc__
        if docstring:
            print(f"\nDocumentation:")
            print(docstring)
        else:
            print("\nDocumentation: No docstring available")
        
        print("-" * 80)


def test_supported_symbols():
    """测试支持的symbol类型"""
    print("\n" + "=" * 80)
    print("SUPPORTED SYMBOL TYPES TEST")
    print("=" * 80)
    
    # Test different symbol types
    test_symbols = {
        "A股": ["600519", "000001", "002415"],
        "美股": ["AAPL", "MSFT", "GOOGL"],
        "加密货币": ["BTC", "ETH", "BNB"],
        "加密货币USD对": ["BTC-USD", "ETH-USD"]
    }
    
    from src.tools.api import get_market_data
    
    for category, symbols in test_symbols.items():
        print(f"\n=== {category} ===")
        for symbol in symbols:
            try:
                result = get_market_data(symbol)
                status = "✓" if result else "✗"
                print(f"  {status} {symbol}: {'SUCCESS' if result else 'FAILED'}")
            except Exception as e:
                print(f"  ✗ {symbol}: ERROR - {str(e)[:50]}...")
        print("-" * 40)


def show_return_data_structure():
    """展示返回数据结构"""
    print("\n" + "=" * 80)
    print("RETURN DATA STRUCTURE EXAMPLES")
    print("=" * 80)
    
    from src.tools.api import get_financial_metrics, get_market_data, get_financial_statements
    
    # Test with a reliable symbol
    test_symbol = "AAPL"
    
    print(f"\n=== TESTING WITH {test_symbol} ===")
    
    # Test get_financial_metrics
    print(f"\n--- get_financial_metrics('{test_symbol}') ---")
    try:
        result = get_financial_metrics(test_symbol)
        print(f"Type: {type(result)}")
        print(f"Length: {len(result) if result else 0}")
        if result and len(result) > 0:
            print("Sample keys:", list(result[0].keys())[:5], "...")
            print("Sample values:", {k: v for k, v in list(result[0].items())[:3]})
    except Exception as e:
        print(f"Error: {e}")
    
    # Test get_market_data
    print(f"\n--- get_market_data('{test_symbol}') ---")
    try:
        result = get_market_data(test_symbol)
        print(f"Type: {type(result)}")
        if result:
            print("Keys:", list(result.keys()))
            print("Sample values:", {k: v for k, v in list(result.items())[:3]})
    except Exception as e:
        print(f"Error: {e}")
    
    # Test get_financial_statements
    print(f"\n--- get_financial_statements('{test_symbol}') ---")
    try:
        result = get_financial_statements(test_symbol)
        print(f"Type: {type(result)}")
        print(f"Length: {len(result) if result else 0}")
        if result and len(result) > 0:
            print("Sample keys:", list(result[0].keys()))
            print("Sample values:", {k: v for k, v in list(result[0].items())[:3]})
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    """运行文档展示测试"""
    print("Enhanced Docstrings Showcase")
    print("=" * 80)
    
    try:
        showcase_enhanced_docstrings()
        test_supported_symbols()
        show_return_data_structure()
        
        print("\n" + "=" * 80)
        print("✅ Enhanced docstrings showcase completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during showcase: {e}")
        import traceback
        traceback.print_exc()