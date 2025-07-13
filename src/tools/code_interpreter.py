# src/tools/code_interpreter.py

import pandas as pd
import numpy as np
import json
from io import StringIO
import sys
import traceback
from typing import Any, Dict, Union
from src.utils.logging_config import setup_logger

logger = setup_logger('code_interpreter')

def python_interpreter(code: str, data: Any = None) -> str:
    """
    在受控的沙箱环境中执行Python代码，用于数据分析。
    
    Args:
        code (str): 要执行的Python代码字符串
        data (Any): 上一步工具返回的数据，代码中可以通过变量访问
        
    Returns:
        str: 代码执行的输出结果或错误信息
        
    注意：这是一个简化的沙箱。生产环境应使用更强的隔离措施（如Docker）。
    """
    logger.info(f"开始执行Python代码，数据类型: {type(data)}")
    
    # 设置沙箱的全局变量，只允许安全的、必要的库和函数
    sandbox_globals = {
        "pd": pd,
        "np": np,
        "json": json,
        "len": len,
        "max": max,
        "min": min,
        "sum": sum,
        "range": range,
        "enumerate": enumerate,
        "zip": zip,
        "sorted": sorted,
        "round": round,
        "abs": abs,
        "str": str,
        "int": int,
        "float": float,
        "list": list,
        "dict": dict,
        "tuple": tuple,
        "set": set,
        "True": True,
        "False": False,
        "None": None,
        "print": print,
        "locals": locals,  # 添加locals函数支持
        "globals": globals,  # 添加globals函数支持
        "__builtins__": {
            "len": len, "max": max, "min": min, "sum": sum, "range": range,
            "enumerate": enumerate, "zip": zip, "sorted": sorted, "round": round,
            "abs": abs, "str": str, "int": int, "float": float, "list": list,
            "dict": dict, "tuple": tuple, "set": set, "print": print,
            "locals": locals, "globals": globals,
        },
    }

    # 准备沙箱的局部变量
    sandbox_locals = {}
    
    # 根据数据类型将数据注入到沙箱中
    if data is not None:
        if isinstance(data, pd.DataFrame):
            sandbox_locals['df'] = data
            logger.info(f"数据已加载为DataFrame，形状: {data.shape}")
        elif isinstance(data, list) and len(data) > 0:
            # 如果是字典列表，尝试转换为DataFrame
            if isinstance(data[0], dict):
                try:
                    df = pd.DataFrame(data)
                    sandbox_locals['df'] = df
                    sandbox_locals['data'] = data  # 同时保留原始数据
                    logger.info(f"字典列表已转换为DataFrame，形状: {df.shape}")
                except Exception as e:
                    sandbox_locals['data'] = data
                    logger.warning(f"无法将数据转换为DataFrame: {e}")
            else:
                sandbox_locals['data'] = data
        elif isinstance(data, dict):
            # 如果是单个字典，看是否包含列表数据
            sandbox_locals['data'] = data
            # 检查是否有'res'或'result'字段包含列表数据
            if 'res' in data and isinstance(data['res'], list) and len(data['res']) > 0:
                if isinstance(data['res'][0], dict):
                    try:
                        df = pd.DataFrame(data['res'])
                        sandbox_locals['df'] = df
                        logger.info(f"从data['res']创建DataFrame，形状: {df.shape}")
                    except Exception as e:
                        logger.warning(f"无法从data['res']创建DataFrame: {e}")
        else:
            sandbox_locals['data'] = data

    # 捕获print输出
    old_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output

    try:
        # 在沙箱中执行代码
        exec(code, sandbox_globals, sandbox_locals)
        
        # 恢复标准输出
        sys.stdout = old_stdout
        
        # 获取执行结果
        if 'result' in sandbox_locals:
            result = sandbox_locals['result']
            logger.info("代码执行成功，找到result变量")
            return str(result)
        else:
            # 如果没有result变量，返回print的内容
            output = redirected_output.getvalue()
            if output.strip():
                logger.info("代码执行成功，返回print输出")
                return output.strip()
            else:
                logger.info("代码执行成功，但没有输出")
                return "代码执行完成，但没有返回值。请确保将结果赋值给'result'变量。"

    except Exception as e:
        sys.stdout = old_stdout
        error_msg = f"代码执行出错: {str(e)}\n详细错误:\n{traceback.format_exc()}"
        logger.error(error_msg)
        return error_msg

def test_code_interpreter():
    """测试代码解释器功能"""
    print("=== 测试代码解释器 ===")
    
    # 测试基本计算
    result1 = python_interpreter("result = 2 + 3")
    print(f"基本计算测试: {result1}")
    
    # 测试pandas操作
    test_data = [
        {"name": "A", "value": 10},
        {"name": "B", "value": 20},
        {"name": "C", "value": 30}
    ]
    
    code = """
avg_value = df['value'].mean()
max_value = df['value'].max()
result = f"平均值: {avg_value}, 最大值: {max_value}"
"""
    
    result2 = python_interpreter(code, test_data)
    print(f"pandas测试: {result2}")
    
    # 测试错误处理
    result3 = python_interpreter("result = undefined_variable")
    print(f"错误处理测试: {result3[:100]}...")

if __name__ == "__main__":
    test_code_interpreter() 