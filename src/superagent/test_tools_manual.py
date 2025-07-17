#!/usr/bin/env python3
"""
Manual test script for Algogene archive tools.
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_docs_reader():
    """Test the documentation reader tool."""
    print("Testing Algogene Documentation Reader...")
    
    try:
        from src.tools.algogene_docs_reader import algogene_docs_reader_tool
        
        # Test 1: Search for API documentation
        print("\n1. Searching for 'API' in documentation:")
        result = algogene_docs_reader_tool._run(query="API")
        print(f"Result length: {len(result)}")
        print(f"Contains 'API': {'API' in result}")
        
        # Test 2: Read a specific file
        print("\n2. Reading specific file '01-overview.md':")
        result = algogene_docs_reader_tool._run(query="", specific_file="01-overview.md")
        print(f"Result length: {len(result)}")
        print(f"Contains 'overview': {'overview' in result.lower()}")
        
        # Test 3: Search for non-existent content
        print("\n3. Searching for non-existent content:")
        result = algogene_docs_reader_tool._run(query="xyz_nonexistent_content")
        print(f"Result length: {len(result)}")
        print(f"Contains suggestion: {'Available documentation files' in result}")
        
        print("✓ Documentation reader tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Documentation reader test failed: {e}")
        return False

def test_code_generator():
    """Test the code generator tool."""
    print("\nTesting Algogene Code Generator...")
    
    try:
        from src.tools.algogene_code_generator import algogene_code_generator_tool
        
        # Test 1: Generate market making strategy
        print("\n1. Generating market making strategy:")
        result = algogene_code_generator_tool._run(
            strategy_name="test_market_making",
            strategy_type="market_making",
            description="Test market making strategy for testing",
            parameters={"spread": 0.01, "volume": 0.05}
        )
        print(f"Result length: {len(result)}")
        print(f"Contains 'generated successfully': {'generated successfully' in result}")
        
        # Test 2: Generate moving average strategy
        print("\n2. Generating moving average strategy:")
        result = algogene_code_generator_tool._run(
            strategy_name="test_moving_average",
            strategy_type="trend_following",
            description="Test moving average strategy for testing",
            parameters={"short_window": 10, "long_window": 30}
        )
        print(f"Result length: {len(result)}")
        print(f"Contains 'generated successfully': {'generated successfully' in result}")
        
        # Test 3: Save provided code
        print("\n3. Saving provided code:")
        test_code = """# Test provided code
print("This is a test strategy")
"""
        result = algogene_code_generator_tool._run(
            strategy_name="test_provided_code",
            strategy_type="custom",
            description="Test strategy with provided code",
            code_content=test_code
        )
        print(f"Result length: {len(result)}")
        print(f"Contains 'saved successfully': {'saved successfully' in result}")
        
        print("✓ Code generator tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Code generator test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Starting Algogene Archive Tools Manual Tests")
    print("=" * 50)
    
    docs_success = test_docs_reader()
    code_success = test_code_generator()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Documentation Reader: {'✓ PASSED' if docs_success else '✗ FAILED'}")
    print(f"Code Generator: {'✓ PASSED' if code_success else '✗ FAILED'}")
    
    if docs_success and code_success:
        print("\n🎉 All tests passed! Tools are working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())