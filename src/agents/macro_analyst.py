from langchain_core.messages import HumanMessage
from src.agents.state import AgentState, show_agent_reasoning, show_workflow_status
from src.tools.news_crawler import get_stock_news
from src.utils.logging_config import setup_logger
from src.utils.api_utils import agent_endpoint, log_llm_interaction
import json
from datetime import datetime, timedelta
from src.tools.openrouter_config import get_chat_completion

# 设置日志记录
logger = setup_logger('macro_analyst_agent')


@agent_endpoint("macro_analyst", "宏观分析师，分析宏观经济环境对目标股票的影响")
def macro_analyst_agent(state: AgentState):
    """负责宏观经济分析"""
    show_workflow_status("Macro Analyst")
    show_reasoning = state["metadata"]["show_reasoning"]
    data = state["data"]
    symbol = data["ticker"]
    logger.info(f"正在进行宏观分析: {symbol}")

    # 获取大量新闻数据（最多100条）
    news_list = get_stock_news(symbol, max_news=100)  # 尝试获取100条新闻

    # 过滤七天前的新闻
    cutoff_date = datetime.now() - timedelta(days=7)
    recent_news = [news for news in news_list
                   if datetime.strptime(news['publish_time'], '%Y-%m-%d %H:%M:%S') > cutoff_date]

    logger.info(f"获取到 {len(recent_news)} 条七天内的新闻")

    # 如果没有获取到新闻，返回默认结果
    if not recent_news:
        logger.warning(f"未获取到 {symbol} 的最近新闻，无法进行宏观分析")
        message_content = {
            "macro_environment": "neutral",
            "impact_on_stock": "neutral",
            "key_factors": [],
            "reasoning": "未获取到最近新闻，无法进行宏观分析"
        }
    else:
        # 获取宏观分析结果
        macro_analysis = get_macro_news_analysis(recent_news)
        message_content = macro_analysis

    # 如果需要显示推理过程
    if show_reasoning:
        show_agent_reasoning(message_content, "Macro Analysis Agent")
        # 保存推理信息到metadata供API使用
        state["metadata"]["agent_reasoning"] = message_content

    # 创建消息
    my_macro_message = HumanMessage(
        content=json.dumps(message_content),
        name="macro_analyst_agent",
    )

    show_workflow_status("Macro Analyst", "completed")
    return {
        "messages": [my_macro_message],
        "data": {
            **data,
            "macro_analysis": message_content
        },
        "metadata": state["metadata"],
    }


def get_macro_news_analysis(news_list: list) -> dict:
    """分析宏观经济新闻对股票的影响

    Args:
        news_list (list): 新闻列表

    Returns:
        dict: 宏观分析结果，包含环境评估、对股票的影响、关键因素和详细推理
    """
    if not news_list:
        return {
            "macro_environment": "neutral",
            "impact_on_stock": "neutral",
            "key_factors": [],
            "reasoning": "没有足够的新闻数据进行宏观分析"
        }

    # 检查缓存
    import os
    cache_file = "src/data/macro_analysis_cache.json"
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    # 生成新闻内容的唯一标识
    news_key = "|".join([
        f"{news['title']}|{news['publish_time']}"
        for news in news_list[:20]  # 使用前20条新闻作为标识
    ])

    # 检查缓存
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                if news_key in cache:
                    logger.info("使用缓存的宏观分析结果")
                    return cache[news_key]
        except Exception as e:
            logger.error(f"读取宏观分析缓存出错: {e}")
            cache = {}
    else:
        logger.info("未找到宏观分析缓存文件，将创建新文件")
        cache = {}

    # # 准备系统消息
    # system_message = {
    #     "role": "system",
    #     "content": """你是一位专业的宏观经济分析师，专注于分析宏观经济环境对A股个股的影响。
    #     请分析提供的新闻，从宏观角度评估当前经济环境，并分析这些宏观因素对目标股票的潜在影响。
    #     回复必须使用英文，不要使用中文或其他语言。
        
    #     请关注以下宏观因素：
    #     1. 货币政策：利率、准备金率、公开市场操作等
    #     2. 财政政策：政府支出、税收政策、补贴等
    #     3. 产业政策：行业规划、监管政策、环保要求等
    #     4. 国际环境：全球经济形势、贸易关系、地缘政治等
    #     5. 市场情绪：投资者信心、市场流动性、风险偏好等
        
    #     你的分析应该包括：
    #     1. 宏观环境评估：积极(positive)、中性(neutral)或消极(negative)
    #     2. 对目标股票的影响：利好(positive)、中性(neutral)或利空(negative)
    #     3. 关键影响因素：列出3-5个最重要的宏观因素
    #     4. 详细推理：解释为什么这些因素会影响目标股票
        
    #     请确保你的分析：
    #     1. 基于事实和数据，而非猜测
    #     2. 考虑行业特性和公司特点
    #     3. 关注中长期影响，而非短期波动
    #     4. 提供具体、可操作的见解"""
    # }
    # Prepare system message in English
    system_message = {
        "role": "system",
        "content": """You are a professional macroeconomic analyst specializing in assessing the impact of macroeconomic environments on stocks listed in either the US or China (A-shares).
Please analyze the provided news articles to evaluate the current macroeconomic environment and its potential impact on the target stock from a macro perspective.
Your reply must be in English only.

Focus on the following macro factors:
1. Monetary policy: interest rates, reserve requirements, open market operations, etc.
2. Fiscal policy: government spending, tax policies, subsidies, etc.
3. Industrial policy: industry planning, regulatory policies, environmental requirements, etc.
4. International environment: global economic conditions, trade relations, geopolitics, etc.
5. Market sentiment: investor confidence, market liquidity, risk appetite, etc.

Your analysis should include:
1. Macroeconomic environment assessment: positive, neutral, or negative
2. Impact on the target stock: positive, neutral, or negative
3. Key influencing factors: list 3-5 most important macro factors
4. Detailed reasoning: explain why these factors affect the target stock

Make sure your analysis:
1. Is based on facts and data, not speculation
2. Considers industry characteristics and company specifics
3. Focuses on medium- and long-term impacts, not short-term fluctuations
4. Provides concrete and actionable insights"""
    }


    # Prepare news content
    news_content = "\n\n".join([
        f"Title: {news['title']}\n"
        f"Source: {news['source']}\n"
        f"Time: {news['publish_time']}\n"
        f"Content: {news['content']}"
        # Use the first 50 news articles for analysis; not 100 to avoid context length issues
        for news in news_list[:50]
    ])

    user_message = {
        "role": "user",
        "content": f"Please analyze the following news articles and assess the current macroeconomic environment and its impact on the relevant A-share listed company:\n\n{news_content}\n\nPlease return the result in JSON format, including the following fields: macro_environment (positive/neutral/negative), impact_on_stock (positive/neutral/negative), key_factors (array), reasoning (detailed reasoning)."
    }

    try:
        # Call LLM for macro analysis
        logger.info("Calling LLM for macro analysis...")
        result = get_chat_completion([system_message, user_message])
        if result is None:
            logger.error("LLM analysis failed, unable to get macro analysis result")
            return {
                "macro_environment": "neutral",
                "impact_on_stock": "neutral",
                "key_factors": [],
                "reasoning": "LLM analysis failed, unable to get macro analysis result"
            }

        # Parse JSON result
        try:
            # Try direct parsing
            analysis_result = json.loads(result.strip())
            logger.info("Successfully parsed JSON result from LLM")
        except json.JSONDecodeError:
            # If direct parsing fails, try extracting JSON part
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
            if json_match:
                try:
                    analysis_result = json.loads(json_match.group(1).strip())
                    logger.info("Successfully extracted and parsed JSON result from code block")
                except:
                    # If still fails, return default result
                    logger.error("Unable to parse JSON result from code block")
                    return {
                        "macro_environment": "neutral",
                        "impact_on_stock": "neutral",
                        "key_factors": [],
                        "reasoning": "Unable to parse JSON result returned by LLM"
                    }
            else:
                # If no JSON found, return default result
                logger.error("LLM did not return a valid JSON format result")
                return {
                    "macro_environment": "neutral",
                    "impact_on_stock": "neutral",
                    "key_factors": [],
                    "reasoning": "LLM did not return a valid JSON format result"
                }

        # Cache result
        cache[news_key] = analysis_result
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            logger.info("Macro analysis result cached")
        except Exception as e:
            logger.error(f"Error writing macro analysis cache: {e}")

        return analysis_result

    except Exception as e:
        logger.error(f"Error during macro analysis: {e}")
        return {
            "macro_environment": "neutral",
            "impact_on_stock": "neutral",
            "key_factors": [],
            "reasoning": f"Error during analysis: {str(e)}"
        }
