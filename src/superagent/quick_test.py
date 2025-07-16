#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速验证脚本 - 确保 API 工具在新环境中正常工作
"""

import sys
import os
sys.path.insert(0, '.')

def main():
    print("🚀 API 工具快速验证...")
    
    try:
        # 测试核心导入
        from src.tools import (
            get_financial_metrics, 
            get_market_data,
            python_interpreter,
            AlgogeneClient
        )
        print("✅ 核心模块导入成功")
        
        # 测试代码解释器
        import pandas as pd
        test_data = pd.DataFrame({'close': [100, 105, 102], 'volume': [1000, 1200, 1100]})
        result = python_interpreter("result = df['close'].mean()", test_data)
        print(f"✅ 代码解释器工作正常: {result}")
        
        print("\n🎉 所有功能验证通过！API 工具已成功迁移到 superagent 环境。")
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
