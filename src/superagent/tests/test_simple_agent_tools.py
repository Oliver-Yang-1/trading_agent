#!/usr/bin/env python3
"""
Simple test to print all tools each agent has access to.
"""

def print_agent_tools():
    """打印每个agent的工具列表"""
    print("=" * 80)
    print("AGENT TOOL ASSIGNMENTS")
    print("=" * 80)
    
    # Define agent tool mappings
    agent_tools = {
        "research_agent": [
            "tavily_tool",
            "crawl_tool"
        ],
        "coder_agent": [
            "python_repl_tool",
            "bash_tool"
        ],
        "data_fetcher_agent": [
            "get_financial_metrics",
            "get_market_data",
            "get_price_history",
            "get_financial_statements"
        ]
    }
    
    # Print each agent's tools
    for agent_name, tools in agent_tools.items():
        print(f"\n=== {agent_name.upper()} ===")
        print(f"Number of tools: {len(tools)}")
        print("Tools:")
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool}")
        print("-" * 60)


def print_tool_details():
    """打印工具详细信息"""
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
    
    print("\n" + "=" * 80)
    print("TOOL DETAILS")
    print("=" * 80)
    
    # Group tools by agent
    agent_tool_objects = {
        "research_agent": [
            ("tavily_tool", tavily_tool),
            ("crawl_tool", crawl_tool),
        ],
        "coder_agent": [
            ("python_repl_tool", python_repl_tool),
            ("bash_tool", bash_tool),
        ],
        "data_fetcher_agent": [
            ("get_financial_metrics", get_financial_metrics),
            ("get_market_data", get_market_data),
            ("get_price_history", get_price_history),
            ("get_financial_statements", get_financial_statements),
        ],
    }
    
    for agent_name, tools in agent_tool_objects.items():
        print(f"\n=== {agent_name.upper()} TOOLS ===")
        
        for tool_name, tool in tools:
            print(f"\n{tool_name}:")
            
            # Handle both LangChain tools and raw functions
            if hasattr(tool, 'name'):
                # LangChain tool
                print(f"  Name: {tool.name}")
                print(f"  Description: {tool.description}")
                print(f"  Type: LangChain Tool")
            else:
                # Raw function
                print(f"  Name: {tool.__name__}")
                print(f"  Description: {tool.__doc__ if tool.__doc__ else 'No description available'}")
                print(f"  Type: Python Function")
                
                # Get function signature
                import inspect
                sig = inspect.signature(tool)
                print(f"  Signature: {sig}")
        
        print("-" * 60)


if __name__ == "__main__":
    """运行工具分析"""
    print("Agent Tools Analysis")
    print("=" * 80)
    
    try:
        print_agent_tools()
        print_tool_details()
        
        print("\n" + "=" * 80)
        print("✅ Agent tools analysis completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()