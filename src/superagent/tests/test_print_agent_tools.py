#!/usr/bin/env python3
"""
Test script to print all tools available to each agent.
This helps understand what capabilities each agent has.
"""

import logging
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_all_tools():
    """打印所有可用工具的详细信息"""
    from src.tools import (
        tavily_tool, 
        crawl_tool, 
        python_repl_tool,
        bash_tool,
        get_financial_metrics,
        get_market_data,
        get_price_history,
        get_financial_statements,
    )
    
    all_tools = [
        ("tavily_tool", tavily_tool),
        ("crawl_tool", crawl_tool),
        ("python_repl_tool", python_repl_tool),
        ("bash_tool", bash_tool),
        ("get_financial_metrics", get_financial_metrics),
        ("get_market_data", get_market_data),
        ("get_price_history", get_price_history),
        ("get_financial_statements", get_financial_statements),
    ]
    
    print("=" * 80)
    print("ALL AVAILABLE TOOLS")
    print("=" * 80)
    
    for tool_name, tool in all_tools:
        print(f"\n=== {tool_name.upper()} ===")
        
        # Handle both LangChain tools and raw functions
        if hasattr(tool, 'name'):
            # LangChain tool
            print(f"Name: {tool.name}")
            print(f"Description: {tool.description}")
            if hasattr(tool, 'args_schema') and tool.args_schema:
                print(f"Args Schema: {tool.args_schema}")
            else:
                print("Args Schema: Not available")
            print(f"Type: LangChain Tool")
        else:
            # Raw function
            print(f"Name: {tool.__name__}")
            print(f"Description: {tool.__doc__ if tool.__doc__ else 'No description available'}")
            
            # Get function signature
            import inspect
            sig = inspect.signature(tool)
            print(f"Signature: {sig}")
            print(f"Type: Python Function")
        
        print("-" * 60)


def print_agent_tools():
    """打印每个agent的工具配置"""
    from src.agents import research_agent, coder_agent, data_fetcher_agent
    
    agents = [
        ("research_agent", research_agent, ["tavily_tool", "crawl_tool"]),
        ("coder_agent", coder_agent, ["python_repl_tool", "bash_tool"]),
        ("data_fetcher_agent", data_fetcher_agent, [
            "get_financial_metrics", 
            "get_market_data", 
            "get_price_history", 
            "get_financial_statements"
        ]),
    ]
    
    print("\n" + "=" * 80)
    print("AGENT TOOL ASSIGNMENTS")
    print("=" * 80)
    
    for agent_name, agent, expected_tools in agents:
        print(f"\n=== {agent_name.upper()} ===")
        print(f"Agent Type: {type(agent)}")
        
        # Try to get tools from the agent
        try:
            if hasattr(agent, 'tools'):
                agent_tools = agent.tools
                print(f"Number of tools: {len(agent_tools)}")
                print("Tools:")
                for i, tool in enumerate(agent_tools, 1):
                    print(f"  {i}. {tool.name}")
                    print(f"     Description: {tool.description}")
                    if hasattr(tool, 'args_schema') and tool.args_schema:
                        print(f"     Args Schema: {tool.args_schema}")
                    print()
            else:
                print("Tools: Could not access tools directly from agent")
                print(f"Expected tools: {expected_tools}")
                
        except Exception as e:
            print(f"Error accessing tools: {e}")
            print(f"Expected tools: {expected_tools}")
        
        print("-" * 60)


def test_individual_tool_functions():
    """测试直接调用工具函数"""
    from src.tools.api import (
        get_financial_metrics,
        get_market_data,
        get_price_history,
        get_financial_statements,
    )
    
    print("\n" + "=" * 80)
    print("INDIVIDUAL TOOL FUNCTION TESTS")
    print("=" * 80)
    
    # Test tool function signatures
    import inspect
    
    tools = [
        ("get_financial_metrics", get_financial_metrics),
        ("get_market_data", get_market_data),
        ("get_price_history", get_price_history),
        ("get_financial_statements", get_financial_statements),
    ]
    
    for tool_name, tool_func in tools:
        print(f"\n=== {tool_name.upper()} ===")
        
        # Get function signature
        sig = inspect.signature(tool_func)
        print(f"Function: {tool_func.__name__}")
        print(f"Signature: {sig}")
        print(f"Docstring: {tool_func.__doc__}")
        
        # Get parameter details
        print("Parameters:")
        for param_name, param in sig.parameters.items():
            print(f"  - {param_name}: {param.annotation} = {param.default}")
        
        # Get return type
        return_annotation = sig.return_annotation
        if return_annotation != inspect.Signature.empty:
            print(f"Returns: {return_annotation}")
        
        print("-" * 60)


def test_tool_creation():
    """测试工具创建过程"""
    from langchain_core.tools import tool
    
    print("\n" + "=" * 80)
    print("TOOL CREATION TEST")
    print("=" * 80)
    
    # Test creating tools from functions
    from src.tools.api import (
        get_financial_metrics,
        get_market_data,
        get_price_history,
        get_financial_statements,
    )
    
    functions = [
        get_financial_metrics,
        get_market_data,
        get_price_history,
        get_financial_statements,
    ]
    
    for func in functions:
        try:
            # Try to create a tool from the function
            created_tool = tool(func)
            print(f"\n✓ Successfully created tool from {func.__name__}")
            print(f"  Tool name: {created_tool.name}")
            print(f"  Tool description: {created_tool.description}")
            if hasattr(created_tool, 'args_schema'):
                print(f"  Args schema: {created_tool.args_schema}")
        except Exception as e:
            print(f"\n✗ Failed to create tool from {func.__name__}: {e}")
            
        print("-" * 40)


def comprehensive_tool_analysis():
    """综合工具分析"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TOOL ANALYSIS")
    print("=" * 80)
    
    # Import all tools
    from src.tools import (
        tavily_tool, 
        crawl_tool, 
        python_repl_tool,
        bash_tool,
        get_financial_metrics,
        get_market_data,
        get_price_history,
        get_financial_statements,
    )
    
    # Categorize tools
    tool_categories = {
        "Research & Search": [
            ("tavily_tool", tavily_tool),
            ("crawl_tool", crawl_tool),
        ],
        "Code Execution": [
            ("python_repl_tool", python_repl_tool),
            ("bash_tool", bash_tool),
        ],
        "Financial Data": [
            ("get_financial_metrics", get_financial_metrics),
            ("get_market_data", get_market_data),
            ("get_price_history", get_price_history),
            ("get_financial_statements", get_financial_statements),
        ],
    }
    
    for category, tools in tool_categories.items():
        print(f"\n=== {category.upper()} ===")
        
        for tool_name, tool in tools:
            print(f"\n{tool_name}:")
            
            # Handle both LangChain tools and raw functions
            if hasattr(tool, 'name'):
                # LangChain tool
                print(f"  Name: {tool.name}")
                description = tool.description
                print(f"  Description: {description[:100]}..." if len(description) > 100 else f"  Description: {description}")
                print(f"  Type: LangChain tool")
            else:
                # Raw function
                print(f"  Name: {tool.__name__}")
                description = tool.__doc__ if tool.__doc__ else 'No description available'
                print(f"  Description: {description[:100]}..." if len(description) > 100 else f"  Description: {description}")
                print(f"  Type: Python function")
        
        print("-" * 60)


if __name__ == "__main__":
    """运行所有工具分析测试"""
    print("Starting Agent Tools Analysis")
    print("=" * 80)
    
    try:
        # Run all analysis functions
        print_all_tools()
        print_agent_tools()
        test_individual_tool_functions()
        test_tool_creation()
        comprehensive_tool_analysis()
        
        print("\n" + "=" * 80)
        print("✅ All tool analysis tests completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during tool analysis: {e}")
        import traceback
        traceback.print_exc()