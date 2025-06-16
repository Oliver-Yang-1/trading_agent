from langchain_core.messages import HumanMessage
from src.agents.state import AgentState, show_agent_reasoning, show_workflow_status
from src.utils.api_utils import agent_endpoint, log_llm_interaction
import json
import ast
# 添加日志记录器 (如果还没有)
from src.utils.logging_config import setup_logger
logger = setup_logger('researcher_bull_agent')

@agent_endpoint("researcher_bull", "多方研究员，从看多角度分析市场数据并提出投资论点")
def researcher_bull_agent(state: AgentState):
    """Analyzes signals from a bullish perspective and generates optimistic investment thesis."""
    show_workflow_status("Bullish Researcher")
    show_reasoning = state["metadata"]["show_reasoning"]

    # Fetch messages from analysts
    technical_message = next(
        (msg for msg in reversed(state["messages"]) if msg.name == "technical_analyst_agent"), None)
    fundamentals_message = next(
        (msg for msg in reversed(state["messages"]) if msg.name == "fundamentals_agent"), None)
    sentiment_message = next(
        (msg for msg in reversed(state["messages"]) if msg.name == "sentiment_agent"), None)
    # valuation_message = next(
    #     msg for msg in state["messages"] if msg.name == "valuation_agent") # Removed
    macro_news_message = next(
        (msg for msg in reversed(state["messages"]) if msg.name == "macro_news_agent"), None) # Added

    # Default signals in case messages are missing
    technical_signals = {"signal": "neutral", "confidence": "0%"}
    fundamental_signals = {"signal": "neutral", "confidence": "0%"}
    sentiment_signals = {"signal": "neutral", "confidence": "0%"}
    macro_news_signals = {"signal": "neutral", "confidence": "0%", "summary": "Macro news data not available."}

    try:
        if technical_message and technical_message.content:
            technical_signals = json.loads(technical_message.content)
        if fundamentals_message and fundamentals_message.content:
            fundamental_signals = json.loads(fundamentals_message.content)
        if sentiment_message and sentiment_message.content:
            sentiment_signals = json.loads(sentiment_message.content)
        # valuation_signals = json.loads(valuation_message.content) # Removed

        if macro_news_message and macro_news_message.content: # Added
            macro_news_signals = json.loads(macro_news_message.content) # Added
    except Exception as e:
        logger.warning(f"Error parsing JSON signals for Bull Researcher: {e}. Trying ast.literal_eval.")
        try:
            if technical_message and technical_message.content and isinstance(technical_message.content, str):
                technical_signals = ast.literal_eval(technical_message.content)
            if fundamentals_message and fundamentals_message.content and isinstance(fundamentals_message.content, str):
                fundamental_signals = ast.literal_eval(fundamentals_message.content)
            if sentiment_message and sentiment_message.content and isinstance(sentiment_message.content, str):
                sentiment_signals = ast.literal_eval(sentiment_message.content)
            # valuation_signals = ast.literal_eval(valuation_message.content) # Removed
            if macro_news_message and macro_news_message.content and isinstance(macro_news_message.content, str): # Added
                macro_news_signals = ast.literal_eval(macro_news_message.content) # Added
        except Exception as e2:
            logger.error(f"Error parsing signals with ast.literal_eval for Bull Researcher: {e2}. Using defaults.")
            # Defaults are already set, so just log

    # Analyze from bullish perspective
    bullish_points = []
    confidence_scores = []

    # Technical Analysis
    if technical_signals["signal"] == "bullish":
        bullish_points.append(
            f"Technical indicators show bullish momentum with {technical_signals['confidence']} confidence")
        confidence_scores.append(
            float(str(technical_signals["confidence"]).replace("%", "")) / 100)
    else:
        bullish_points.append(
            "Technical indicators may be conservative, presenting buying opportunities")
        confidence_scores.append(0.3)

    # Fundamental Analysis
    if fundamental_signals["signal"] == "bullish":
        bullish_points.append(
            f"Strong fundamentals with {fundamental_signals['confidence']} confidence")
        confidence_scores.append(
            float(str(fundamental_signals["confidence"]).replace("%", "")) / 100)
    else:
        bullish_points.append(
            "Company fundamentals show potential for improvement")
        confidence_scores.append(0.3)

    # Sentiment Analysis
    if sentiment_signals.get("signal") == "bullish":
        bullish_points.append(
            f"Positive market sentiment with {sentiment_signals.get('confidence', 'N/A')} confidence")
        try:
            confidence_scores.append(
                float(str(sentiment_signals.get("confidence", "0%")).replace("%", "")) / 100)
        except ValueError:
            confidence_scores.append(0.5) # Default if parsing fails
    else:
        bullish_points.append(
            "Market sentiment may be overly pessimistic, creating value opportunities")
        confidence_scores.append(0.3)

    # Valuation Analysis # Removed section
    # if valuation_signals.get("signal") == "bullish":
    #     bullish_points.append(
    #         f"Stock appears undervalued with {valuation_signals.get('confidence', 'N/A')} confidence")
    #     try:
    #         confidence_scores.append(
    #             float(str(valuation_signals.get("confidence", "0%")).replace("%", "")) / 100)
    #     except ValueError:
    #         confidence_scores.append(0.5) # Default if parsing fails
    # else:
    #     bullish_points.append(
    #         "Current valuation may not fully reflect growth potential")
    #     confidence_scores.append(0.3)

    # Macro News Analysis # Added section
    macro_signal = macro_news_signals.get("signal", "neutral")
    macro_confidence_str = str(macro_news_signals.get("confidence", "0%"))
    # Try to get a summary, fallback to reasoning if summary key doesn't exist
    macro_summary = macro_news_signals.get("policy_impact_summary", 
                                          macro_news_signals.get("market_outlook_short_term",
                                          "No specific macro summary provided."))

    if macro_signal == "bullish":
        bullish_points.append(
            f"Supportive macroeconomic news/environment. Summary: {macro_summary} (Confidence: {macro_confidence_str})")
        try:
            confidence_scores.append(
                float(macro_confidence_str.replace("%", "")) / 100)
        except ValueError:
            confidence_scores.append(0.6) # Default positive confidence
    elif macro_signal == "neutral":
        bullish_points.append(
            f"Neutral macroeconomic news/environment, allowing other bullish factors to dominate. Summary: {macro_summary} (Confidence: {macro_confidence_str})")
        try:
            # Neutral macro news has less impact on confidence for a directional bet
            confidence_scores.append(
                (float(macro_confidence_str.replace("%", "")) / 100) * 0.5)
        except ValueError:
            confidence_scores.append(0.3)
    else:  # Bearish macro news
        bullish_points.append(
            f"Despite potentially challenging macroeconomic news (Summary: {macro_summary}, Confidence: {macro_confidence_str}), other factors drive a bullish outlook.")
        # Bearish macro news might temper bullish enthusiasm slightly or be considered less impactful than stock-specific factors
        confidence_scores.append(0.2) # Lower confidence contribution

    # Calculate overall bullish confidence
    avg_confidence = sum(confidence_scores) / len(confidence_scores)

    message_content = {
        "perspective": "bullish",
        "confidence": avg_confidence,
        "thesis_points": bullish_points,
        "reasoning": "Bullish thesis based on comprehensive analysis of technical, fundamental, sentiment, and macro news factors" # Updated
    }

    message = HumanMessage(
        content=json.dumps(message_content),
        name="researcher_bull_agent",
    )

    if show_reasoning:
        show_agent_reasoning(message_content, "Bullish Researcher")
        # 保存推理信息到metadata供API使用
        state["metadata"]["agent_reasoning"] = message_content

    show_workflow_status("Bullish Researcher", "completed")
    return {
        "messages": state["messages"] + [message],
        "data": state["data"],
        "metadata": state["metadata"],
    }
