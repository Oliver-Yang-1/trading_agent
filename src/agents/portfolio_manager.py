from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
import json
from src.utils.logging_config import setup_logger

from src.agents.state import AgentState, show_agent_reasoning, show_workflow_status
from src.tools.openrouter_config import get_chat_completion
from src.utils.api_utils import agent_endpoint, log_llm_interaction

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
    """Responsible for portfolio management"""
    agent_name = "portfolio_management_agent"
    logger.info(f"\n--- DEBUG: {agent_name} START ---")

    # Log raw incoming messages
    # logger.info(
    # f"--- DEBUG: {agent_name} RAW INCOMING messages: {[msg.name for msg in state['messages']]} ---")
    # for i, msg in enumerate(state['messages']):
    #     logger.info(
    #         f"  DEBUG RAW MSG {i}: name='{msg.name}', content_preview='{str(msg.content)[:100]}...'")

    # Clean and unique messages by agent name, taking the latest if duplicates exist
    # This is crucial because this agent is a sink for multiple paths.
    unique_incoming_messages = {}
    for msg in state["messages"]:
        # Keep overriding with later messages to get the latest by name
        unique_incoming_messages[msg.name] = msg

    cleaned_messages_for_processing = list(unique_incoming_messages.values())
    # logger.info(
    # f"--- DEBUG: {agent_name} CLEANED messages for processing: {[msg.name for msg in cleaned_messages_for_processing]} ---")

    show_workflow_status(f"{agent_name}: --- Executing Portfolio Manager ---")
    show_reasoning_flag = state["metadata"]["show_reasoning"]
    portfolio = state["data"]["portfolio"]

    # Get messages from other agents using the cleaned list
    technical_message = get_latest_message_by_name(
        cleaned_messages_for_processing, "technical_analyst_agent")
    fundamentals_message = get_latest_message_by_name(
        cleaned_messages_for_processing, "fundamentals_agent")
    sentiment_message = get_latest_message_by_name(
        cleaned_messages_for_processing, "sentiment_agent")
    risk_message = get_latest_message_by_name(
        cleaned_messages_for_processing, "risk_management_agent")
    tool_based_macro_message = get_latest_message_by_name(
        cleaned_messages_for_processing, "macro_analyst_agent")  # This is the main analysis path output

    # Extract content, handling potential None if message not found by get_latest_message_by_name
    technical_content = technical_message.content if technical_message else json.dumps(
        {"signal": "error", "details": "Technical message missing"})
    fundamentals_content = fundamentals_message.content if fundamentals_message else json.dumps(
        {"signal": "error", "details": "Fundamentals message missing"})
    sentiment_content = sentiment_message.content if sentiment_message else json.dumps(
        {"signal": "error", "details": "Sentiment message missing"})
    risk_content = risk_message.content if risk_message else json.dumps(
        {"signal": "error", "details": "Risk message missing"})
    tool_based_macro_content = tool_based_macro_message.content if tool_based_macro_message else json.dumps(
        {"signal": "error", "details": "Tool-based Macro message missing"})

    # Market-wide news summary from macro_news_agent (already correctly fetched from state["data"])
    market_wide_news_summary_content = state["data"].get(
        "macro_news_analysis_result", "大盘宏观新闻分析不可用或未提供。")
    # Optional: also try to get the message object for consistency in agent_signals, though data field is primary source
    macro_news_agent_message_obj = get_latest_message_by_name(
        cleaned_messages_for_processing, "macro_news_agent")

    system_message_content = """You are a portfolio manager making final trading decisions.
            Your job is to make a trading decision based on the team's analysis while strictly adhering
            to risk management constraints.

            RISK MANAGEMENT CONSTRAINTS:
            - You MUST NOT exceed the max_position_size specified by the risk manager
            - You MUST follow the trading_action (buy/sell/hold) recommended by risk management
            - These are hard constraints that cannot be overridden by other signals

            When weighing the different signals for direction and timing:
            1. Fundamental Analysis (Weight 35%)
            2. Technical Analysis (Weight 30%)
            3. Macro Analysis (Weight 25%) - This encompasses TWO inputs:
               a) General Macro Environment (from Macro Analyst Agent, tool-based)
               b) Daily Market-Wide News Summary (from Macro News Agent)
               Both provide context for external risks and opportunities.
            4. Sentiment Analysis (Weight 10%)
            
            The decision process should be:
            1. First check risk management constraints
            2. Then evaluate fundamentals signal
            3. Consider BOTH the General Macro Environment AND the Daily Market-Wide News Summary.
            4. Use technical analysis for timing
            5. Consider sentiment for final adjustment
           
            Provide the following in your output JSON:
            - "action": "buy" | "sell" | "hold",
            - "quantity": <positive integer>
            - "confidence": <float between 0 and 1>
            - "agent_signals": <list of agent signals including agent name, signal (bullish | bearish | neutral), and their confidence>.
              IMPORTANT: Your 'agent_signals' list MUST include entries for:
                - "technical_analysis"
                - "fundamental_analysis"
                - "sentiment_analysis"
                - "risk_management"
                - "selected_stock_macro_analysis" (representing the tool-based macro input from macro_analyst_agent)
                - "market_wide_news_summary(SH and SZ 300 Index)" (representing the daily news summary input from macro_news_agent - provide a brief signal like bullish/bearish/neutral for the news summary itself, or state if it was primarily factored into overall reasoning with confidence reflecting its impact)
            - "reasoning": <concise explanation of the decision including how you weighted ALL signals, including both macro inputs>

            Trading Rules:
            - Never exceed risk management position limits
            - Only buy if you have available cash
            - Only sell if you have shares to sell
            - Quantity must be ≤ current position for sells
            - Quantity must be ≤ max_position_size from risk management"""
    system_message = {
        "role": "system",
        "content": system_message_content
    }

    user_message_content = f"""Based on the team's analysis below, make your trading decision.

            Technical Analysis Signal: {technical_content}
            Fundamental Analysis Signal: {fundamentals_content}
            Sentiment Analysis Signal: {sentiment_content}
            Risk Management Signal: {risk_content}
            General Macro Analysis (from Macro Analyst Agent): {tool_based_macro_content}
            Daily Market-Wide News Summary (from Macro News Agent):
            {market_wide_news_summary_content}

            Current Portfolio:
            Cash: {portfolio['cash']:.2f}
            Current Position: {portfolio['stock']} shares

            Output JSON only. Ensure 'agent_signals' includes all required agents as per system prompt."""
    user_message = {
        "role": "user",
        "content": user_message_content
    }

    show_agent_reasoning(
        agent_name, f"Preparing LLM. User msg includes: TA, FA, Sent, Risk, GeneralMacro, MarketNews.")

    llm_interaction_messages = [system_message, user_message]
    llm_response_content = get_chat_completion(llm_interaction_messages)

    current_metadata = state["metadata"]
    current_metadata["current_agent_name"] = agent_name

    def get_llm_result_for_logging_wrapper():
        return llm_response_content
    log_llm_interaction(state)(get_llm_result_for_logging_wrapper)()

    if llm_response_content is None:
        show_agent_reasoning(
            agent_name, "LLM call failed. Using default conservative decision.")
        # Ensure the dummy response matches the expected structure for agent_signals
        llm_response_content = json.dumps({
            "action": "hold",
            "quantity": 0,
            "confidence": 0.7,
            "agent_signals": [
                {"agent_name": "technical_analysis",
                    "signal": "neutral", "confidence": 0.0},
                {"agent_name": "fundamental_analysis",
                    "signal": "neutral", "confidence": 0.0},
                {"agent_name": "sentiment_analysis",
                    "signal": "neutral", "confidence": 0.0},
                # {"agent_name": "valuation_analysis", # Removed
                #     "signal": "neutral", "confidence": 0.0}, # Removed
                {"agent_name": "risk_management",
                    "signal": "hold", "confidence": 1.0},
                {"agent_name": "macro_analyst_agent",
                    "signal": "neutral", "confidence": 0.0},
                {"agent_name": "macro_news_agent",
                    "signal": "unavailable_or_llm_error", "confidence": 0.0}
            ],
            "reasoning": "LLM API error. Defaulting to conservative hold based on risk management."
        })

    final_decision_message = HumanMessage(
        content=llm_response_content,
        name=agent_name,
    )

    if show_reasoning_flag:
        show_agent_reasoning(
            agent_name, f"Final LLM decision JSON: {llm_response_content}")

    agent_decision_details_value = {}
    try:
        decision_json = json.loads(llm_response_content)
        agent_decision_details_value = {
            "action": decision_json.get("action"),
            "quantity": decision_json.get("quantity"),
            "confidence": decision_json.get("confidence"),
            "reasoning_snippet": decision_json.get("reasoning", "")[:150] + "..."
        }
    except json.JSONDecodeError:
        agent_decision_details_value = {
            "error": "Failed to parse LLM decision JSON from portfolio manager",
            "raw_response_snippet": llm_response_content[:200] + "..."
        }

    show_workflow_status(f"{agent_name}: --- Portfolio Manager Completed ---")

    # The portfolio_management_agent is a terminal or near-terminal node in terms of new message generation for the main state.
    # It should return its own decision, and an updated state["messages"] that includes its decision.
    # As it's a汇聚点, it should ideally start with a cleaned list of messages from its inputs.
    # The cleaned_messages_for_processing already did this. We append its new message to this cleaned list.

    # If we strictly want to follow the pattern of `state["messages"] + [new_message]` for all non-leaf nodes,
    # then the `cleaned_messages_for_processing` should become the new `state["messages"]` for this node's context.
    # However, for simplicity and robustness, let's assume its output `messages` should just be its own message added to the cleaned input it processed.

    final_messages_output = cleaned_messages_for_processing + [final_decision_message]
    # Alternative if we want to be super strict about adding to the raw incoming state["messages"]:
    # final_messages_output = state["messages"] + [final_decision_message]
    # But this ^ is prone to the duplication we are trying to solve if not careful.
    # The most robust is that portfolio_manager provides its clear output, and the graph handles accumulation if needed for further steps (none in this case as it's END).

    # logger.info(
    # f"--- DEBUG: {agent_name} RETURN messages: {[msg.name for msg in final_messages_output]} ---")

    return {
        "messages": final_messages_output,
        "data": state["data"],
        "metadata": {
            **state["metadata"],
            f"{agent_name}_decision_details": agent_decision_details_value,
            "agent_reasoning": llm_response_content
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
