#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基本的 API 测试脚本
"""

import sys
import os

# 添加当前项目路径到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """测试所有必要模块的导入"""
    try:
        from src.tools.api import get_financial_metrics, get_market_data, get_price_history
        print("✅ API 模块导入成功")
        
        from src.tools.algogene_client import AlgogeneClient
        print("✅ AlgogeneClient 导入成功")
        
        from src.tools.news_crawler import get_stock_news, get_news_sentiment
        print("✅ 新闻爬虫模块导入成功")
        
        from src.tools.openrouter_config import get_chat_completion
        print("✅ OpenRouter 配置模块导入成功")
        
        from src.tools.data_analyzer import analyze_stock_data
        print("✅ 数据分析模块导入成功")
        
        from src.tools.code_interpreter import python_interpreter
        print("✅ 代码解释器模块导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    try:
        from src.tools.api import get_market_data
        
        # 测试获取市场数据（使用简单的美股代码）
        print("\n🧪 测试获取市场数据...")
        result = get_market_data("AAPL")
        if result:
            print("✅ 获取市场数据成功")
            print(f"   示例数据: {list(result.keys())[:3]}...")
        else:
            print("⚠️  获取市场数据返回空结果")
        
        return True
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始 API 基础测试...\n")
    
    # 测试导入
    import_success = test_imports()
    
    if import_success:
        # 测试基本功能
        print("\n" + "="*50)
        test_basic_functionality()
    
    print("\n" + "="*50)
    print("✅ 测试完成!" if import_success else "❌ 测试失败!")
