"""
ReAct Super Node Agent - 使用推理-行动(Reasoning-Acting)模式的超级智能节点

这个agent实现了ReAct模式，能够：
1. 观察当前状态
2. 推理下一步应该采取的行动
3. 执行相应的工具调用
4. 观察结果并继续推理
5. 重复直到获得最终答案

ReAct模式参考: https://github.com/langchain-ai/react-agent
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.state import AgentState, show_agent_reasoning, show_workflow_status
from src.tools.openrouter_config import get_chat_completion
from src.utils.api_utils import agent_endpoint, log_llm_interaction
from src.utils.logging_config import setup_logger

# 导入可用的工具
from src.tools.api import get_financial_metrics, get_financial_statements, get_market_data, get_price_history
from src.tools.news_crawler import get_stock_news, get_news_sentiment
# 导入Algogene包装函数
from src.tools.algogene_client import get_algogene_price_history, get_algogene_realtime_price

# 设置日志记录
logger = setup_logger('super_node_agent')

# 定义可用的工具
AVAILABLE_TOOLS = {
    "get_financial_metrics": {
        "function": get_financial_metrics,
        "description": """获取股票的综合财务指标数据。返回13个关键财务指标:
        
        盈利能力指标:
        - return_on_equity: 净资产收益率 (ROE)
        - net_margin: 销售净利率
        - operating_margin: 营业利润率
        
        增长指标:
        - revenue_growth: 营收增长率
        - earnings_growth: 净利润增长率  
        - book_value_growth: 净资产增长率
        
        财务健康指标:
        - current_ratio: 流动比率
        - debt_to_equity: 资产负债率
        - free_cash_flow_per_share: 每股经营性现金流
        - earnings_per_share: 每股收益
        
        估值比率:
        - pe_ratio: 市盈率 (P/E)
        - price_to_book: 市净率 (P/B)
        - price_to_sales: 市销率 (P/S)
        
        适用于: 基本面分析、价值投资评估、财务健康度检查""",
        "parameters": ["symbol: str - 股票代码，如'600519'(贵州茅台)"]
    },
    "get_financial_statements": {
        "function": get_financial_statements, 
        "description": """获取股票的财务报表数据，包含最新期间和上一期间的对比数据。
        
        返回数据包含:
        - net_income: 净利润
        - operating_revenue: 营业收入
        - operating_profit: 营业利润
        - working_capital: 营运资金 (流动资产-流动负债)
        - depreciation_and_amortization: 折旧摊销
        - capital_expenditure: 资本支出
        - free_cash_flow: 自由现金流 (经营现金流-资本支出)
        
        数据来源: 利润表、资产负债表、现金流量表
        适用于: 财务分析、现金流分析、盈利能力评估""",
        "parameters": ["symbol: str - 股票代码，如'000001'(平安银行)"]
    },
    "get_market_data": {
        "function": get_market_data,
        "description": """获取股票的实时市场交易数据和基本市场信息。
        
        返回数据包含:
        - market_cap: 总市值 (元)
        - volume: 当日成交量 (手)
        - average_volume: 平均成交量 (手)
        - fifty_two_week_high: 52周最高价 (元)
        - fifty_two_week_low: 52周最低价 (元)
        
        数据更新频率: 实时
        适用于: 市场概况分析、流动性评估、价格区间分析""",
        "parameters": ["symbol: str - 股票代码，如'300059'(东方财富)"]
    },
    "get_price_history": {
        "function": get_price_history,
        "description": """获取股票的历史价格数据，包含丰富的技术指标。默认获取过去一年数据。
        
        基础价格数据:
        - date, open, high, low, close: 日期和四价
        - volume, amount: 成交量和成交额
        - amplitude, pct_change, turnover: 振幅、涨跌幅、换手率
        
        技术指标:
        - 动量指标: momentum_1m, momentum_3m, momentum_6m, volume_momentum
        - 波动率指标: historical_volatility, volatility_regime, volatility_z_score, atr_ratio  
        - 统计指标: hurst_exponent, skewness, kurtosis
        
        复权类型: 'qfq'前复权(默认), 'hfq'后复权, ''不复权
        适用于: 技术分析、量化策略、趋势分析、风险评估""",
        "parameters": [
            "symbol: str - 股票代码，如'000858'(五粮液)", 
            "start_date: str - 开始日期 'YYYY-MM-DD'，默认一年前",
            "end_date: str - 结束日期 'YYYY-MM-DD'，默认昨天",
            "adjust: str - 复权类型，默认'qfq'前复权"
        ]
    },
    "get_stock_news": {
        "function": get_stock_news,
        "description": """获取股票相关的最新新闻信息，支持缓存机制避免重复请求。
        
        返回新闻包含:
        - title: 新闻标题
        - content: 新闻内容  
        - publish_time: 发布时间
        - source: 新闻来源
        - url: 新闻链接
        - keyword: 关键词
        
        数据特点:
        - 按发布时间倒序排列 (最新在前)
        - 自动过滤内容过短的新闻
        - 当日新闻自动缓存，避免重复请求
        - 最大支持100条新闻
        
        适用于: 基本面分析、事件驱动分析、舆情监控""",
        "parameters": [
            "symbol: str - 股票代码，如'002415'(海康威视)",
            "max_news: int - 获取新闻数量，默认10条，最大100条"
        ]
    },
    "get_news_sentiment": {
        "function": get_news_sentiment,
        "description": """使用AI模型分析新闻的情感倾向，专门针对A股市场特点进行优化。
        
        情感分数范围 [-1, 1]:
        - 1.0: 极其积极 (重大利好消息、超预期业绩、行业政策支持)
        - 0.5-0.9: 积极 (业绩增长、新项目落地、获得订单)
        - 0.1-0.4: 轻微积极 (小额合同签订、日常经营正常)
        - 0.0: 中性 (日常公告、人事变动、无重大影响的新闻)
        - -0.1~-0.4: 轻微消极 (小额诉讼、非核心业务亏损)
        - -0.5~-0.9: 消极 (业绩下滑、重要客户流失、行业政策收紧)
        - -1.0: 极其消极 (重大违规、核心业务严重亏损、被监管处罚)
        
        分析维度: 业绩相关、政策影响、市场表现、资本运作、风险事件、行业地位、舆论环境
        
        缓存机制: 相同新闻组合的分析结果会被缓存，提高效率
        适用于: 情绪分析、舆情监控、事件影响评估""",
        "parameters": [
            "news_list: list - 新闻列表，来自get_stock_news的返回结果",
            "num_of_news: int - 分析的新闻数量，默认5条，建议3-10条"
        ]
    },
    "get_algogene_price_history": {
        "function": get_algogene_price_history,
        "description": """通过Algogene API获取指定交易工具的历史价格数据。
        
        返回数据包含完整的OHLC蜡烛图数据:
        - t: 时间戳 (GMT+0格式: YYYY-MM-DD HH:MM:SS)
        - o, h, l, c: 开盘价、最高价、最低价、收盘价
        - b, a, m: 收盘买价、卖价、中间价
        - v: 交易量
        - instrument: 交易工具名称
        
        支持多种时间间隔:
        - 'M': 分钟级数据
        - 'H': 小时级数据  
        - 'D': 日级数据
        - 'W': 周级数据
        - 'MN': 月级数据
        
        适用于: 技术分析、回测研究、量化策略开发、全球市场数据分析""",
        "parameters": [
            "count: int - 获取数据点数量",
            "instrument: str - 交易工具符号，如'AAPL'、'EURUSD'、'BTCUSD'等",
            "interval: str - 时间间隔，如'M'(分钟)、'H'(小时)、'D'(日)等",
            "timestamp: str - 参考时间戳，格式'YYYY-MM-DD HH:MM:SS'"
        ]
    },
    "get_algogene_realtime_price": {
        "function": get_algogene_realtime_price,
        "description": """通过Algogene API获取指定金融工具的实时市场报价数据。
        
        返回实时市场数据:
        - timestamp: UTC+0时间戳
        - bidPrice/askPrice: 实时买价/卖价
        - bidSize/askSize: 买盘/卖盘数量
        - bidOrderBook/askOrderBook: 买卖盘深度
        
        支持的经纪商:
        - 'diginex': Diginex经纪商
        - 'exness': Exness经纪商
        - 'ib': Interactive Brokers
        - 'ig': IG Markets
        - 'oanda': OANDA
        - 默认: 所有可用经纪商中的最新数据
        
        支持多种资产类型: 股票、外汇、加密货币、大宗商品等
        适用于: 实时交易、价差监控、流动性分析、套利机会发现""",
        "parameters": [
            "symbols: str - 金融符号列表，用逗号分隔，如'BTCUSD,ETHUSD'或'AAPL,GOOGL'",
            "broker: Optional[str] - 指定经纪商(可选)，如'ib'、'oanda'等"
        ]
    }
}

def safe_json_serialize(obj):
    """安全的JSON序列化函数，处理pandas和numpy对象"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, date
    
    # 先检查具体类型，避免对DataFrame直接使用pd.isna()
    if obj is None:
        return None
    elif isinstance(obj, pd.DataFrame):
        # 检查DataFrame是否为空
        if obj.empty:
            return []
        # 先转换DataFrame为dict，然后递归处理每个值
        try:
            df_dict = obj.to_dict('records')
            return safe_json_serialize(df_dict)
        except Exception as e:
            logger.warning(f"DataFrame序列化失败，转为字符串: {e}")
            return f"DataFrame with {len(obj)} rows and {len(obj.columns)} columns"
    elif isinstance(obj, pd.Series):
        # 先转换Series为dict，然后递归处理每个值
        try:
            series_dict = obj.to_dict()
            return safe_json_serialize(series_dict)
        except Exception as e:
            logger.warning(f"Series序列化失败，转为字符串: {e}")
            return f"Series with {len(obj)} values"
    elif isinstance(obj, (pd.Timestamp, datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return [safe_json_serialize(item) for item in obj.tolist()]
    elif isinstance(obj, dict):
        return {str(key): safe_json_serialize(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [safe_json_serialize(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    else:
        # 安全地检查pandas NA值 - 只对未知类型的标量值使用
        try:
            if hasattr(pd, 'isna') and np.isscalar(obj) and pd.isna(obj):
                return None
        except (TypeError, ValueError):
            # 如果pd.isna检查失败，继续处理
            pass
        
        # 检查是否为其他可迭代对象（但不是字符串）
        try:
            if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
                # 对于可迭代对象，尝试转换为列表
                return [safe_json_serialize(item) for item in obj]
        except (TypeError, ValueError):
            # 如果转换失败，继续到最后的处理
            pass
        
        # 最后的fallback处理
        try:
            # 尝试直接序列化
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            # 如果不能序列化，转换为字符串
            return str(obj)

def format_tools_for_llm() -> str:
    """格式化工具信息供LLM理解"""
    tools_info = []
    for tool_name, tool_info in AVAILABLE_TOOLS.items():
        params = ", ".join(tool_info["parameters"])
        tools_info.append(f"- {tool_name}({params}): {tool_info['description']}")
    return "\n".join(tools_info)

def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """执行指定的工具"""
    if tool_name not in AVAILABLE_TOOLS:
        return f"Error: Tool '{tool_name}' not found"
    
    try:
        tool_function = AVAILABLE_TOOLS[tool_name]["function"]
        result = tool_function(**arguments)
        logger.info(f"Tool '{tool_name}' executed successfully")
        return result
    except Exception as e:
        error_msg = f"Error executing tool '{tool_name}': {str(e)}"
        logger.error(error_msg)
        return error_msg

def parse_action(response: str) -> Optional[Dict[str, Any]]:
    """解析LLM响应中的行动指令
    
    期望格式:
    Action: tool_name
    Action Input: {"param1": "value1", "param2": "value2"}
    """
    try:
        lines = response.strip().split('\n')
        action_line = None
        input_line = None
        
        for line in lines:
            if line.startswith("Action:"):
                action_line = line.replace("Action:", "").strip()
            elif line.startswith("Action Input:"):
                input_line = line.replace("Action Input:", "").strip()
        
        if action_line and input_line:
            try:
                # 尝试解析JSON参数
                action_input = json.loads(input_line)
                return {
                    "tool": action_line,
                    "arguments": action_input
                }
            except json.JSONDecodeError:
                # 如果不是JSON，尝试简单解析
                return {
                    "tool": action_line,
                    "arguments": {"symbol": input_line}  # 默认作为symbol参数
                }
    except Exception as e:
        logger.error(f"Error parsing action: {e}")
    
    return None

def is_final_answer(response: str) -> bool:
    """判断响应是否包含最终答案"""
    return "Final Answer:" in response or "最终答案:" in response

def extract_final_answer(response: str) -> str:
    """提取最终答案"""
    if "Final Answer:" in response:
        return response.split("Final Answer:")[-1].strip()
    elif "最终答案:" in response:
        return response.split("最终答案:")[-1].strip()
    return response

@agent_endpoint("super_node", "超级ReAct节点，使用推理-行动模式进行智能分析")
def super_node_agent(state: AgentState) -> AgentState:
    """
    超级ReAct节点 - 使用推理-行动模式
    
    这个agent会：
    1. 分析当前状态和用户查询
    2. 推理需要采取的行动
    3. 执行工具调用获取信息
    4. 分析结果并决定下一步
    5. 重复直到得出最终答案
    """
    show_workflow_status("Super ReAct Node")
    show_reasoning = state["metadata"]["show_reasoning"]
    
    data = state["data"]
    
    # 从用户消息中提取任务
    user_query = ""
    if state["messages"]:
        # 找到最后一个用户消息
        for msg in reversed(state["messages"]):
            if hasattr(msg, 'name') and msg.name == "user":
                user_query = msg.content
                break
    
    # 如果没有找到用户查询，使用默认任务
    if not user_query:
        user_query = "请介绍你的功能和能力"
    
    # ReAct系统提示
    system_prompt = f"""你是一个智能助手，使用ReAct(Reasoning and Acting)模式执行各种任务。

你可以帮助用户完成各种分析和任务，包括但不限于：
- 股票和金融分析
- 数据收集和处理  
- 信息查询和整理
- 计算和推理任务
- 内容分析和生成

当前用户任务: {user_query}

可用工具:
{format_tools_for_llm()}

请按照以下格式进行推理和行动:

Thought: [你的思考过程，分析当前情况，决定下一步行动]
Action: [工具名称]
Action Input: {{"参数名": "参数值"}}
Observation: [工具执行结果，由系统自动填入]

重复上述过程直到你有足够信息给出最终答案，然后:

Final Answer: [你的最终分析结论和建议]

开始执行任务:
Query: {user_query}
"""

    # 初始化对话历史
    conversation_history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    
    # ReAct循环
    max_iterations = 5  # 最大迭代次数
    iteration = 0
    observations = []
    
    while iteration < max_iterations:
        iteration += 1
        logger.info(f"ReAct迭代 {iteration}/{max_iterations}")
        
        try:
            # 获取LLM响应
            llm_response = log_llm_interaction(state)(
                lambda: get_chat_completion(conversation_history)
            )()
            
            # 安全检查LLM响应
            if llm_response is None or (isinstance(llm_response, str) and not llm_response.strip()):
                break
                
            logger.info(f"LLM Response: {llm_response[:200]}...")
            
            # 检查是否是最终答案
            if is_final_answer(llm_response):
                final_answer = extract_final_answer(llm_response)
                logger.info("ReAct循环完成，获得最终答案")
                break
            
            # 解析行动
            action = parse_action(llm_response)
            if not action:
                # 如果无法解析行动，尝试直接使用响应作为思考过程
                conversation_history.append({"role": "assistant", "content": llm_response})
                conversation_history.append({"role": "user", "content": "请继续分析，如果需要更多信息，请指定具体的Action和Action Input。"})
                continue
            
            # 执行工具
            tool_name = action["tool"]
            arguments = action["arguments"]
            
            # 对于需要symbol参数的金融工具，尝试从用户查询中提取股票代码
            if "symbol" not in arguments and tool_name in ["get_financial_metrics", "get_financial_statements", "get_market_data", "get_price_history", "get_stock_news"]:
                # 尝试从用户查询中提取股票代码
                import re
                # 匹配常见的股票代码格式
                stock_patterns = [
                    r'\b([A-Z]{1,5})\b',  # 美股代码 (如 AAPL)
                    r'\b(\d{6})\b',       # A股代码 (如 000001)
                    r'\b(\d{3}\d{3})\b'   # 其他6位数字代码
                ]
                
                extracted_symbol = None
                for pattern in stock_patterns:
                    matches = re.findall(pattern, user_query.upper())
                    if matches:
                        extracted_symbol = matches[0]
                        break
                
                if extracted_symbol:
                    arguments["symbol"] = extracted_symbol
                    logger.info(f"从用户查询中提取到股票代码: {extracted_symbol}")
                else:
                    logger.warning(f"工具 {tool_name} 需要股票代码参数，但未能从查询中提取到")
                    # 可以选择跳过此工具或要求用户提供更多信息
                
            logger.info(f"执行工具: {tool_name} with args: {arguments}")
            observation = execute_tool(tool_name, arguments)
            
            # 如果observation是DataFrame，提前进行安全检查
            if isinstance(observation, pd.DataFrame):
                logger.info(f"检测到DataFrame结果，包含 {len(observation)} 行数据")
                # 直接处理DataFrame，避免后续的布尔判断问题
                if observation.empty:
                    safe_observation = []
                else:
                    safe_observation = safe_json_serialize(observation)
            else:
                # 安全序列化观察结果
                safe_observation = safe_json_serialize(observation)
            
            # 格式化观察结果
            if isinstance(safe_observation, (list, dict)):
                observation_text = json.dumps(safe_observation, indent=2, ensure_ascii=False)
            else:
                observation_text = str(safe_observation)
            
            observations.append({
                "tool": tool_name,
                "arguments": arguments,
                "result": safe_observation
            })
            
            # 更新对话历史
            conversation_history.append({"role": "assistant", "content": llm_response})
            conversation_history.append({"role": "user", "content": f"Observation: {observation_text}\n\n请继续你的分析。"})
            
        except Exception as e:
            logger.error(f"ReAct迭代 {iteration} 出错: {e}")
            break
    
    # 如果没有得到最终答案，生成一个基于观察的总结
    if 'final_answer' not in locals():
        # 安全序列化观察结果用于总结
        try:
            safe_observations = safe_json_serialize(observations)
        except Exception as e:
            logger.error(f"序列化observations失败: {e}")
            safe_observations = []
        
        summary_prompt = f"""基于以下工具执行结果，请给出分析总结:

观察结果:
{json.dumps(safe_observations, indent=2, ensure_ascii=False)}

请提供分析结论和建议。"""
        
        try:
            final_response = log_llm_interaction(state)(
                lambda: get_chat_completion([
                    {"role": "system", "content": "你是专业的股票分析师，请基于数据给出分析结论。"},
                    {"role": "user", "content": summary_prompt}
                ])
            )()
            final_answer = final_response if final_response else "分析完成，但无法生成最终结论。"
        except Exception as e:
            logger.error(f"生成最终答案失败: {e}")
            final_answer = "分析过程中遇到技术问题，请稍后重试。"
    
    # 构建分析结果并安全序列化
    analysis_result = {
        "user_query": user_query,
        "analysis_type": "ReAct Super Node Analysis",
        "iterations": iteration,
        "tools_used": [obs["tool"] for obs in observations],
        "final_answer": final_answer,
        "observations": observations if show_reasoning else []
    }
    
    # 安全序列化分析结果
    safe_analysis_result = safe_json_serialize(analysis_result)
    
    if show_reasoning:
        show_agent_reasoning(safe_analysis_result, "Super ReAct Node")
        state["metadata"]["agent_reasoning"] = safe_analysis_result
    
    # 创建响应消息，确保所有内容都可以JSON序列化
    message_content = {
        "signal": "analysis_complete",
        "confidence": "high",
        "reasoning": final_answer,
        "analysis_result": safe_analysis_result
    }
    
    message = HumanMessage(
        content=json.dumps(safe_json_serialize(message_content), ensure_ascii=False),
        name="super_node_agent"
    )
    
    show_workflow_status("Super ReAct Node", "completed")
    
    return {
        "messages": [message],
        "data": {
            **data,
            "super_node_analysis": safe_analysis_result
        },
        "metadata": state["metadata"]
    } 