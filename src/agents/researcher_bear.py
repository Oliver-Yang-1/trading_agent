from langchain_core.messages import HumanMessage
from src.agents.state import AgentState, show_agent_reasoning, show_workflow_status
from src.utils.api_utils import agent_endpoint, log_llm_interaction
import json
import ast
# 添加日志记录器 (如果还没有)
from src.utils.logging_config import setup_logger
logger = setup_logger('researcher_bear_agent')

@agent_endpoint("researcher_bear", "空方研究员，从看空角度分析市场数据并提出风险警示")
def researcher_bear_agent(state: AgentState):
    """Analyzes signals from a bearish perspective and generates cautionary investment thesis."""
    show_workflow_status("Bearish Researcher")
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
        logger.warning(f"Error parsing JSON signals for Bear Researcher: {e}. Trying ast.literal_eval.")
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
            logger.error(f"Error parsing signals with ast.literal_eval for Bear Researcher: {e2}. Using defaults.")
            # Defaults are already set, so just log

    # Analyze from bearish perspective
    bearish_points = []
    confidence_scores = []

    # Technical Analysis
    if technical_signals["signal"] == "bearish":
        bearish_points.append(
            f"Technical indicators show bearish momentum with {technical_signals['confidence']} confidence")
        confidence_scores.append(
            float(str(technical_signals["confidence"]).replace("%", "")) / 100)
    else:
        bearish_points.append(
            "Technical rally may be temporary, suggesting potential reversal")
        confidence_scores.append(0.3)

    # Fundamental Analysis
    if fundamental_signals["signal"] == "bearish":
        bearish_points.append(
            f"Concerning fundamentals with {fundamental_signals['confidence']} confidence")
        confidence_scores.append(
            float(str(fundamental_signals["confidence"]).replace("%", "")) / 100)
    else:
        bearish_points.append(
            "Current fundamental strength may not be sustainable")
        confidence_scores.append(0.3)

    # Sentiment Analysis
    if sentiment_signals.get("signal") == "bearish":
        bearish_points.append(
            f"Negative market sentiment with {sentiment_signals.get('confidence', 'N/A')} confidence")
        try:
            confidence_scores.append(
                float(str(sentiment_signals.get("confidence", "0%")).replace("%", "")) / 100)
        except ValueError:
            confidence_scores.append(0.5) # Default if parsing fails
    else:
        bearish_points.append(
            "Market sentiment may be overly optimistic, indicating potential risks")
        confidence_scores.append(0.3)

    # Valuation Analysis # Removed section
    # if valuation_signals.get("signal") == "bearish":
    #     bearish_points.append(
    #         f"Stock appears overvalued with {valuation_signals.get('confidence', 'N/A')} confidence")
    #     try:
    #         confidence_scores.append(
    #             float(str(valuation_signals.get("confidence", "0%")).replace("%", "")) / 100)
    #     except ValueError:
    #         confidence_scores.append(0.5) # Default if parsing fails
    # else:
    #     bearish_points.append(
    #         "Current valuation may not fully reflect downside risks")
    #     confidence_scores.append(0.3)

    # Macro News Analysis # Added section
    macro_signal = macro_news_signals.get("signal", "neutral")
    macro_confidence_str = str(macro_news_signals.get("confidence", "0%"))
    macro_summary = macro_news_signals.get("summary", macro_news_signals.get("reasoning", "No specific macro summary provided."))

    if macro_signal == "bearish":
        bearish_points.append(
            f"Concerning macroeconomic news/environment. Summary: {macro_summary} (Confidence: {macro_confidence_str})")
        try:
            confidence_scores.append(
                float(macro_confidence_str.replace("%", "")) / 100)
        except ValueError:
            confidence_scores.append(0.6) # Default positive confidence for bearish signal
    elif macro_signal == "neutral":
        bearish_points.append(
            f"Neutral macroeconomic news/environment, other factors drive bearish outlook. Summary: {macro_summary} (Confidence: {macro_confidence_str})")
        try:
            confidence_scores.append(
                (float(macro_confidence_str.replace("%", "")) / 100) * 0.5)
        except ValueError:
            confidence_scores.append(0.3)
    else:  # Bullish macro news
        bearish_points.append(
            f"Despite potentially positive macroeconomic news (Summary: {macro_summary}, Confidence: {macro_confidence_str}), other factors indicate a bearish outlook.")
        # Bullish macro news might be seen as a temporary distraction or insufficient to counter stock-specific bearish factors
        confidence_scores.append(0.2) # Lower confidence contribution

    # Calculate overall bearish confidence
    avg_confidence = sum(confidence_scores) / len(confidence_scores)

    message_content = {
        "perspective": "bearish",
        "confidence": avg_confidence,
        "thesis_points": bearish_points,
        "reasoning": "Bearish thesis based on comprehensive analysis of technical, fundamental, sentiment, and macro news factors" # Updated
    }

    message = HumanMessage(
        content=json.dumps(message_content),
        name="researcher_bear_agent",
    )

    if show_reasoning:
        show_agent_reasoning(message_content, "Bearish Researcher")
        # 保存推理信息到metadata供API使用
        state["metadata"]["agent_reasoning"] = message_content

    show_workflow_status("Bearish Researcher", "completed")
    return {
        "messages": state["messages"] + [message],
        "data": state["data"],
        "metadata": state["metadata"],
    }
