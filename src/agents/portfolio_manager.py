from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
import json
from src.utils.logging_config import setup_logger

from src.agents.state import AgentState, show_agent_reasoning, show_workflow_status
from src.tools.openrouter_config import get_chat_completion
from src.utils.api_utils import agent_endpoint, log_llm_interaction

from src.tools.crypto_symbols import CRYPTO_SYMBOLS
# 初始化 logger
logger = setup_logger('portfolio_management_agent')

##### Portfolio Management Agent #####

# Helper function to get the latest message by agent name


def get_latest_message_by_name(messages: list, name: str):
    for msg in reversed(messages):
        if msg.name == name:
            return msg
    logger.warning(
        f"Message from agent '{name}' not found in portfolio_management_agent.")
    # Return a dummy message object or raise an error, depending on desired handling
    # For now, returning a dummy message to avoid crashing, but content will be None.
    return HumanMessage(content=json.dumps({"signal": "error", "details": f"Message from {name} not found"}), name=name)


@agent_endpoint("portfolio_management", "负责投资组合管理和最终交易决策")
def portfolio_management_agent(state: AgentState):
    agent_name = "portfolio_management_agent"
    show_workflow_status(f"{agent_name}: --- Executing Portfolio Management Agent ---")

    # 获取所有上游agent的最新消息内容
    messages = state.get("messages", [])
    data = state.get("data", {})
    
    # 新增：获取当前交易的品种 (symbol)
    symbol = data.get("ticker", "UNKNOWN").upper()
    # 新增：判断是否为加密货币
    is_crypto = symbol in CRYPTO_SYMBOLS # 可以根据需要扩展这个列表

    # 技术分析
    technical_analysis_msg = next((m.content for m in reversed(messages) if m.name == "technical_analyst_agent"), "技术分析结果不可用。")
    # 基本面分析
    fundamentals_analysis_msg = next((m.content for m in reversed(messages) if m.name == "fundamentals_agent"), "基本面分析结果不可用。")
    # 情绪分析
    sentiment_analysis_msg = next((m.content for m in reversed(messages) if m.name == "sentiment_agent"), "情绪分析结果不可用。")
    # 研究员 (牛市或熊市)
    researcher_bull_msg = next((m.content for m in reversed(messages) if m.name == "researcher_bull_agent"), None)
    researcher_bear_msg = next((m.content for m in reversed(messages) if m.name == "researcher_bear_agent"), None)
    researcher_analysis_msg = researcher_bull_msg or researcher_bear_msg or "研究员分析结果不可用。"
    
    # 宏观新闻分析 (从 state["data"] 获取解析后的字典)
    macro_news_data = data.get("macro_news_analysis_result") # This should be a dictionary
    macro_news_summary_for_llm = "宏观新闻分析不可用或未提供。"
    macro_sentiment_signal = "neutral" # Default
    macro_sentiment_confidence = 0.0 # Default

    if isinstance(macro_news_data, dict):
        macro_sentiment_signal = macro_news_data.get("overall_sentiment", "neutral")
        macro_sentiment_confidence = macro_news_data.get("sentiment_confidence", 0.0)
        key_themes = ", ".join(macro_news_data.get("key_hot_sectors_or_themes", []))
        potential_risks = ", ".join(macro_news_data.get("key_potential_risks", []))
        policy_impact = macro_news_data.get("policy_impact_summary", "N/A")
        market_outlook = macro_news_data.get("market_outlook_short_term", "N/A")
        # detailed_report = macro_news_data.get("detailed_analysis_report", "详细报告不可用。") # 可选，如果prompt需要完整报告

        macro_news_summary_for_llm = (
            f"Overall Sentiment: {macro_sentiment_signal} (Confidence: {macro_sentiment_confidence:.2f}).\n"
            f"Key Themes/Sectors: {key_themes if key_themes else 'None identified'}.\n"
            f"Potential Risks: {potential_risks if potential_risks else 'None identified'}.\n"
            f"Policy Impact: {policy_impact}.\n"
            f"Market Outlook: {market_outlook}."
            # f"Detailed Report Snippet: {detailed_report[:200]}..." # 仅传递摘要或关键点给LLM
        )
    elif isinstance(macro_news_data, str) : # Fallback if it's somehow still a string (e.g. old cache not converted)
        try:
            # Try to parse if it's a JSON string
            parsed_data_fallback = json.loads(macro_news_data)
            if isinstance(parsed_data_fallback, dict) and "detailed_analysis_report" in parsed_data_fallback:
                 # It was a JSON string of the new format
                macro_sentiment_signal = parsed_data_fallback.get("overall_sentiment", "neutral")
                macro_sentiment_confidence = parsed_data_fallback.get("sentiment_confidence", 0.0)
                # ... (repopulate other fields as above) ...
                macro_news_summary_for_llm = f"Overall Sentiment: {macro_sentiment_signal} (Confidence: {macro_sentiment_confidence:.2f}) ... [Data from fallback string parse]"
            else: # It was some other string
                macro_news_summary_for_llm = f"宏观新闻分析（原始文本）: {macro_news_data[:300]}..." # Truncate if it's plain text
        except json.JSONDecodeError: # It's plain text
             macro_news_summary_for_llm = f"宏观新闻分析（原始文本）: {macro_news_data[:300]}..."


    current_portfolio = data.get("portfolio", {"cash": 100000, "stock": 0, "avg_price": 0, "unrealized_pnl": 0, "portfolio_value":100000})
    current_portfolio_str = json.dumps(current_portfolio, ensure_ascii=False)

    # 新增：为加密货币和股票构建不同的指令
    asset_specific_instructions = ""
    if is_crypto:
        asset_specific_instructions = f"""
IMPORTANT: You are currently trading a cryptocurrency ({symbol}). Follow these specific rules:
1.  **Quantity is a float, not an integer.** The 'quantity' field in your JSON response MUST be the exact fractional number representing the amount of the coin to trade FOR THIS TIME, NOT THE TOTAL AMOUNT. DO NOT divide by 100 or adjust this number in any way.

2.  **Extract the current price from Technical Analysis.** You MUST carefully review the Technical Analysis report to find and use the ACTUAL CURRENT PRICE of {symbol}. Do not use arbitrary price assumptions.

3.  **Calculate quantity based on available cash and actual price.** If you decide to "buy":
    - First, determine what percentage of available cash to invest (typically 10-50% depending on conviction)
    - Then calculate: quantity = (cash * investment_percentage) / current_price
    - CRITICAL: The exact result of this calculation should be your 'quantity' value in the JSON response
    - Example: If cash is $100,000, you invest 20% ($20,000), and price is $30,000, then quantity = 0.667
    - Your JSON would include: "quantity": 0.667  (NOT 0.00667, NOT 66.7, EXACTLY 0.667)

4.  **Ignore Fundamental Analysis.** Cryptocurrency lacks traditional financial statements. The `fundamentals_agent`'s analysis will likely be empty or irrelevant. You MUST ignore its output and give it zero weight in your decision-making process.

5.  **Focus on other signals.** Base your decision primarily on Technical Analysis, Sentiment Analysis, and Macro trends.

6.  **Include your price finding and calculation in reasoning.** In your "reasoning" field, explicitly state: "Based on Technical Analysis, the current price of {symbol} is $X. Investing Y% of available cash ($Z) gives a quantity of A. This A is my final quantity value."
"""
    else:
        asset_specific_instructions = f"""
IMPORTANT: You are currently trading a stock ({symbol}). Follow these specific rules:
1.  **Quantity is an integer.** The 'quantity' must be a whole number (e.g., 100, 200).
2.  **Consider all analysis.** Give appropriate weight to all agent inputs, including Fundamental, Technical, Sentiment, and Macro analysis.
"""

    # 构建系统提示词
    system_message_content = f"""You are the Portfolio Manager of a hedge fund team. Your responsibility is to make the final trading decision based on the team's analysis for the asset: {symbol}.

{asset_specific_instructions}

Team Members Analysis:
- "technical_analyst_agent": (Provides technical indicators and price signals)
- "fundamentals_agent": (Provides fundamental analysis and value insights)
- "sentiment_agent": (Provides sentiment analysis from news and social media)
- "macro_news_agent": (Provides structured macro market analysis including overall_sentiment, sentiment_confidence, key_themes, risks, and outlook)
- "researcher_bull_agent" or "researcher_bear_agent": (Provides focused research based on supervisor's direction)

Current Portfolio: {current_portfolio_str}

Your decision must be one of: "buy", "sell", or "hold".
If "buy" or "sell", specify "quantity". For "hold", quantity should be 0.
The "confidence" score should be between 0.0 and 1.0.

Provide your analysis in JSON format only, with no other text or explanations:
{{
    "action": "buy|sell|hold",
    "quantity": "<integer_for_stocks_or_float_for_crypto>",
    "confidence": "<float, 0.0-1.0>",
    "reasoning": "<brief explanation of your decision, considering all inputs and asset-specific rules>",
    "agent_signals": [
        {{"agent_name": "technical_analyst_agent", "signal": "<parsed_signal_or_summary>", "confidence": "<parsed_confidence_or_default>"}},
        {{"agent_name": "fundamentals_agent", "signal": "<parsed_signal_or_summary>", "confidence": "<parsed_confidence_or_default>"}},
        {{"agent_name": "sentiment_agent", "signal": "<parsed_signal_or_summary>", "confidence": "<parsed_confidence_or_default>"}},
        {{"agent_name": "macro_news_agent", "signal": "{macro_sentiment_signal}", "confidence": {macro_sentiment_confidence}}},
        {{"agent_name": "researcher_bull_agent_or_researcher_bear_agent", "signal": "<parsed_signal_or_summary>", "confidence": "<parsed_confidence_or_default>"}}
    ]
}}"""

    # 构建用户消息内容
    user_message_content = f"""Based on the team's analysis below for {symbol}, make your trading decision.
    
Technical Analysis (from technical_analyst_agent):
{technical_analysis_msg}

Fundamentals Analysis (from fundamentals_agent):
{fundamentals_analysis_msg}

Sentiment Analysis (from sentiment_agent):
{sentiment_analysis_msg}

Macro News Analysis (from macro_news_agent):
{macro_news_summary_for_llm}

Focused Research (from researcher_bull_agent or researcher_bear_agent):
{researcher_analysis_msg}

Current Portfolio: {current_portfolio_str}

Output JSON only. Ensure 'agent_signals' includes all required agents as per system prompt, using their actual signals and confidences if available, or a neutral summary otherwise.
For 'macro_news_agent' in 'agent_signals', use the overall_sentiment as its signal and sentiment_confidence as its confidence.
"""

    show_agent_reasoning(
        f"System Prompt for LLM:\n{system_message_content}", agent_name)
    show_agent_reasoning(
        f"User Message for LLM:\n{user_message_content}", agent_name)

    llm_response_content = "{\"action\": \"hold\", \"quantity\": 0, \"confidence\": 0.5, \"reasoning\": \"Default hold due to LLM call issue.\", \"agent_signals\": []}"
    try:
        response = get_chat_completion(
            messages=[
                {"role": "system", "content": system_message_content},
                {"role": "user", "content": user_message_content}
            ]
        )
        if response:
            llm_response_content = response.strip()
            # Ensure it's valid JSON, remove markdown if any
            if llm_response_content.startswith("```json"):
                llm_response_content = llm_response_content[7:]
            if llm_response_content.endswith("```"):
                llm_response_content = llm_response_content[:-3]
            llm_response_content = llm_response_content.strip()
            
            # Validate JSON
            try:
                json.loads(llm_response_content) # Test parsing
            except json.JSONDecodeError as je:
                logger.error(f"{agent_name}: LLM returned invalid JSON for portfolio decision: {llm_response_content[:200]}... Error: {je}")
                # Fallback to a default hold decision if JSON is malformed
                llm_response_content = json.dumps({
                    "action": "hold", "quantity": 0, "confidence": 0.1, 
                    "reasoning": f"LLM response was not valid JSON. Original: {llm_response_content[:100]}",
                    "agent_signals": [
                        {"agent_name": "technical_analyst_agent", "signal": "error_parsing_llm", "confidence": 0.0},
                        {"agent_name": "fundamentals_agent", "signal": "error_parsing_llm", "confidence": 0.0},
                        {"agent_name": "sentiment_agent", "signal": "error_parsing_llm", "confidence": 0.0},
                        {"agent_name": "macro_news_agent", "signal": macro_sentiment_signal, "confidence": macro_sentiment_confidence}, # Use parsed macro
                        {"agent_name": "researcher_bull_agent_or_researcher_bear_agent", "signal": "error_parsing_llm", "confidence": 0.0}
                    ]
                })

        else:
            logger.error(f"{agent_name}: LLM call returned no response.")
            # llm_response_content remains the default hold
            
    except Exception as e:
        logger.error(f"{agent_name}: Exception during LLM call: {e}")
        # llm_response_content remains the default hold

    show_agent_reasoning(
        f"LLM Response (Portfolio Decision JSON):\n{llm_response_content}", agent_name)
    
    # 将决策结果添加到消息列表，并更新状态
    # The content of the HumanMessage should be the JSON string of the decision
    final_decision_message = HumanMessage(content=llm_response_content, name=agent_name)
    
    # The data stored in AgentState should be the parsed dictionary of the decision
    try:
        final_decision_dict = json.loads(llm_response_content)
    except json.JSONDecodeError:
        logger.error(f"{agent_name}: Could not parse final_decision_content to dict. Storing raw string.")
        final_decision_dict = {"error": "Failed to parse final decision JSON", "raw_response": llm_response_content}


    agent_details_for_metadata = {
        "llm_decision_json_preview": llm_response_content[:150] + "..." if len(llm_response_content) > 150 else llm_response_content,
        "inputs_considered": {
            "technical": technical_analysis_msg[:100]+"...",
            "fundamentals": fundamentals_analysis_msg[:100]+"...",
            "sentiment": sentiment_analysis_msg[:100]+"...",
            "macro_news": macro_news_summary_for_llm[:100]+"...",
            "researcher": researcher_analysis_msg[:100]+"..."
        }
    }

    show_workflow_status(f"{agent_name}: Execution finished.")
    return {
        "messages": messages + [final_decision_message], # Add new decision message
        "data": {**data, "final_portfolio_decision": final_decision_dict}, # Store parsed decision dict
        "metadata": {
            **state["metadata"],
            f"{agent_name}_details": agent_details_for_metadata
        }
    }


def format_decision(action: str, quantity: int, confidence: float, agent_signals: list, reasoning: str, market_wide_news_summary: str = "未提供") -> dict:
    """Format the trading decision into a standardized output format.
    Think in English but output analysis in Chinese."""

    fundamental_signal = next(
        (s for s in agent_signals if s["agent_name"] == "fundamental_analysis"), None)
    technical_signal = next(
        (s for s in agent_signals if s["agent_name"] == "technical_analysis"), None)
    sentiment_signal = next(
        (s for s in agent_signals if s["agent_name"] == "sentiment_analysis"), None)
    risk_signal = next(
        (s for s in agent_signals if s["agent_name"] == "risk_management"), None)
    # Existing macro signal from macro_analyst_agent (tool-based)
    general_macro_signal = next(
        (s for s in agent_signals if s["agent_name"] == "macro_analyst_agent"), None)
    # New market-wide news summary signal from macro_news_agent
    market_wide_news_signal = next(
        (s for s in agent_signals if s["agent_name"] == "macro_news_agent"), None)

    # def signal_to_chinese(signal_data):
    #     if not signal_data:
    #         return "无数据"
    #     if signal_data.get("signal") == "bullish":
    #         return "看多"
    #     if signal_data.get("signal") == "bearish":
    #         return "看空"
    #     return "中性"

    def signal_to_english(signal_data):
        if not signal_data:
            return "No data"
        if signal_data.get("signal") == "bullish":
            return "Bullish"
        if signal_data.get("signal") == "bearish":
            return "Bearish"
        return "Neutral"

    detailed_analysis = f"""
====================================
          Investment Analysis Report
====================================

I. Strategy Analysis

1. Fundamental Analysis (Weight 30%):
   Signal: {signal_to_english(fundamental_signal)}
   Confidence: {fundamental_signal['confidence']*100:.0f if fundamental_signal else 0}%
   Key Points:
   - Profitability: {fundamental_signal.get('reasoning', {}).get('profitability_signal', {}).get('details', 'No data') if fundamental_signal else 'No data'}
   - Growth: {fundamental_signal.get('reasoning', {}).get('growth_signal', {}).get('details', 'No data') if fundamental_signal else 'No data'}
   - Financial Health: {fundamental_signal.get('reasoning', {}).get('financial_health_signal', {}).get('details', 'No data') if fundamental_signal else 'No data'}
   - Valuation Level: {fundamental_signal.get('reasoning', {}).get('price_ratios_signal', {}).get('details', 'No data') if fundamental_signal else 'No data'}

3. Technical Analysis (Weight 25%)
   Signal: {signal_to_english(technical_signal)}
   Confidence: {technical_signal['confidence']*100:.0f if technical_signal else 0}%
   Key Points:
   - Trend Following: ADX={technical_signal.get('strategy_signals', {}).get('trend_following', {}).get('metrics', {}).get('adx', 0.0):.2f if technical_signal else 0.0:.2f}
   - Mean Reversion: RSI(14)={technical_signal.get('strategy_signals', {}).get('mean_reversion', {}).get('metrics', {}).get('rsi_14', 0.0):.2f if technical_signal else 0.0:.2f}
   - Momentum Indicators:
     * 1M Momentum={technical_signal.get('strategy_signals', {}).get('momentum', {}).get('metrics', {}).get('momentum_1m', 0.0):.2% if technical_signal else 0.0:.2%}
     * 3M Momentum={technical_signal.get('strategy_signals', {}).get('momentum', {}).get('metrics', {}).get('momentum_3m', 0.0):.2% if technical_signal else 0.0:.2%}
     * 6M Momentum={technical_signal.get('strategy_signals', {}).get('momentum', {}).get('metrics', {}).get('momentum_6m', 0.0):.2% if technical_signal else 0.0:.2%}
   - Volatility: {technical_signal.get('strategy_signals', {}).get('volatility', {}).get('metrics', {}).get('historical_volatility', 0.0):.2% if technical_signal else 0.0:.2%}

4. Macro Analysis (Total Weight 15%): 
   a) General Macro Analysis (from Macro Analyst Agent):
      Signal: {signal_to_english(general_macro_signal)}
      Confidence: {general_macro_signal['confidence']*100:.0f if general_macro_signal else 0}%
      Macro Environment: {general_macro_signal.get(
          'macro_environment', 'No data') if general_macro_signal else 'No data'}
      Impact on Stock: {general_macro_signal.get(
          'impact_on_stock', 'No data') if general_macro_signal else 'No data'}
      Key Factors: {', '.join(general_macro_signal.get(
          'key_factors', ['No data']) if general_macro_signal else ['No data'])}

   b) Market-wide News Analysis (from Macro News Agent):
      Signal: {signal_to_english(market_wide_news_signal)}
      Confidence: {market_wide_news_signal['confidence']*100:.0f if market_wide_news_signal else 0}%
      Summary or Conclusion: {market_wide_news_signal.get(
          'reasoning', market_wide_news_summary) if market_wide_news_signal else market_wide_news_summary}

5. Sentiment Analysis (Weight 10%):
   Signal: {signal_to_english(sentiment_signal)}
   Confidence: {sentiment_signal['confidence']*100:.0f if sentiment_signal else 0}%
   Analysis: {sentiment_signal.get('reasoning', 'No detailed analysis')
                             if sentiment_signal else 'No detailed analysis'}

II. Risk Assessment
Risk Score: {risk_signal.get('risk_score', 'No data') if risk_signal else 'No data'}/10
Key Metrics:
- Volatility: {risk_signal.get('risk_metrics', {}).get('volatility', 0.0)*100:.1f if risk_signal else 0.0}%
- Max Drawdown: {risk_signal.get('risk_metrics', {}).get('max_drawdown', 0.0)*100:.1f if risk_signal else 0.0}%
- VaR(95%): {risk_signal.get('risk_metrics', {}).get('value_at_risk_95', 0.0)*100:.1f if risk_signal else 0.0}%
- Market Risk: {risk_signal.get('risk_metrics', {}).get('market_risk_score', 'No data') if risk_signal else 'No data'}/10

III. Investment Recommendation
Action: {'Buy' if action == 'buy' else 'Sell' if action == 'sell' else 'Hold'}
Trade Quantity: {quantity} shares
Decision Confidence: {confidence*100:.0f}%

IV. Decision Rationale
{reasoning}

===================================="""

    return {
        "action": action,
        "quantity": quantity,
        "confidence": confidence,
        "agent_signals": agent_signals,
        # "分析报告": detailed_analysis,
        "analysis_report": detailed_analysis
    }
