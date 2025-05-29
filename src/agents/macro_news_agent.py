import os
import json
from datetime import datetime
import akshare as ak
from src.utils.logging_config import setup_logger
# from langgraph.graph import AgentState # Changed import
# Added for alignment
from src.agents.state import AgentState, show_agent_reasoning, show_workflow_status
from typing import Dict, Any, List
from src.utils.api_utils import agent_endpoint  # Added for alignment
from src.tools.openrouter_config import get_chat_completion
from langchain_core.messages import HumanMessage  # Added import

# LLM Prompt for analyzing full news data
LLM_PROMPT_MACRO_ANALYSIS = """You are a senior macro analyst specializing in the A-share (China) market. Based on the **full set of news data** for the CSI 300 Index (symbol: 000300) for today provided below, conduct a thorough analysis and generate a professional macro summary report.

Your report should cover the following aspects:
1.  **Market Sentiment Interpretation**: Provide an overall assessment of current market sentiment (e.g., optimistic, cautious, pessimistic) and briefly explain your reasoning.
2.  **Hot Sector Identification**: Identify 1-3 major hot sectors or themes reflected in the news, and explain their driving factors.
3.  **Potential Risk Alerts**: Highlight 1-2 potential macro or market-level risks that may be implied in the news.
4.  **Policy Impact Analysis**: If important policy changes are mentioned in the news, analyze their possible short-term and long-term impacts on the market.
5.  **Comprehensive Outlook**: Based on the above analysis, provide a concise outlook for the short-term market trend.

Ensure your analysis is objective, logically structured, and uses professional language. Return only the analysis report content—do not include any extra explanations or polite phrases.
Your reply must be in English only. Do not use Chinese or any other language.

# **Today's news data is as follows:**
{news_data_json_string}
"""

# Initialize logger
logger = setup_logger('macro_news_agent')


@agent_endpoint("macro_news_agent", "Fetch full CSI 300 news and conduct macro analysis to provide a market-level macro environment assessment for investment decisions")
def macro_news_agent(state: AgentState) -> Dict[str, Any]:
    """
    Fetch full CSI 300 news, call LLM for macro analysis, and save the result.
    This Agent runs independently, does not depend on specific upstream data, and injects results into AgentState.
    """
    agent_name = "macro_news_agent"
    show_workflow_status(f"{agent_name}: --- Executing Macro News Agent ---")
    symbol = "000300"  # CSI 300 Index
    news_list_for_llm: List[Dict[str, str]] = []
    summary = f"An unknown error occurred during macro news analysis."  # Default error summary
    retrieved_news_count = 0
    from_cache = False  # Flag to indicate if summary was loaded from cache

    today_str = datetime.now().strftime("%Y-%m-%d")
    output_file_path = os.path.join("src", "data", "macro_summary.json")

    # Attempt to load from cache first
    if os.path.exists(output_file_path):
        try:
            with open(output_file_path, 'r', encoding='utf-8') as f:
                all_summaries = json.load(f)
            if today_str in all_summaries and all_summaries[today_str].get("summary_content"):
                cached_data = all_summaries[today_str]
                summary = cached_data["summary_content"]
                retrieved_news_count = cached_data.get(
                    "retrieved_news_count", 0)  # Get cached news count
                from_cache = True
                show_workflow_status(
                    f"{agent_name}: Loaded macro news summary for {today_str} from cache.")
                show_agent_reasoning(
                    f"Loaded macro summary for {today_str} from cache. News count: {retrieved_news_count}", agent_name)
        except json.JSONDecodeError:
            show_agent_reasoning(
                f"JSONDecodeError for {output_file_path} when trying to load cache. Will fetch fresh data.", agent_name)
            all_summaries = {}  # Reset if file is corrupt
        except Exception as e:
            show_agent_reasoning(
                f"Error loading cache from {output_file_path}: {str(e)}. Will fetch fresh data.", agent_name)
            all_summaries = {}  # Reset on other errors

    if not from_cache:
        show_workflow_status(f"{agent_name}: No summary found in cache for today or cache is invalid, fetching real-time news.")
        try:
            show_workflow_status(
                f"{agent_name}: Fetching news for symbol {symbol}")
            news_df = ak.stock_news_em(symbol=symbol)
            if news_df is None or news_df.empty:
                message = f"No news data retrieved for {symbol}."
                show_workflow_status(f"{agent_name}: {message}")
                show_agent_reasoning(
                    f"No news found for {symbol}. Proceeding with no data summary.", agent_name)
                summary = "No macro news data available today." 
            else:
                retrieved_news_count = len(news_df)
                message = f"Successfully retrieved {retrieved_news_count} news items for {symbol}."
                show_workflow_status(f"{agent_name}: {message}")
                show_agent_reasoning(
                    f"Successfully fetched {retrieved_news_count} news items for {symbol}. Preparing for LLM analysis.", agent_name)
                for _, row in news_df.iterrows():
                    news_item = {
                        "title": str(row.get("新闻标题", "")).strip(),
                        "content": str(row.get("新闻内容", "")).strip(),  # Full content
                        "publish_time": str(row.get("发布时间", "")).strip()
                    }
                    news_list_for_llm.append(news_item)

                news_data_json_string = json.dumps(
                    news_list_for_llm, ensure_ascii=False, indent=2)
                prompt_filled = LLM_PROMPT_MACRO_ANALYSIS.format(
                    news_data_json_string=news_data_json_string
                )

                show_workflow_status(
                    f"{agent_name}: Calling LLM for analysis.")
                llm_response = get_chat_completion(
                    messages=[{"role": "user", "content": prompt_filled}]
                )
                summary = llm_response.strip() if llm_response else "LLM analysis failed to return valid results."
                show_workflow_status(f"{agent_name}: LLM macro analysis result obtained successfully.")
                show_agent_reasoning(
                    f"LLM analysis complete. Summary (first 100 chars): {summary[:100]}...", agent_name)

        except Exception as e:
            error_message = f"{agent_name}: Exception occurred: {e}"
            show_workflow_status(error_message)
            show_agent_reasoning(
                f"Exception during execution: {str(e)}", agent_name)
            summary = f"An error occurred during macro news analysis: {str(e)}"

    # Save summary to JSON file (only if not from cache and successful, or if updating existing)
    if not from_cache:
        show_workflow_status(
            f"{agent_name}: Preparing to save summary to {output_file_path}")

        # Ensure all_summaries is initialized if cache loading failed or file didn't exist
        if not os.path.exists(output_file_path) or 'all_summaries' not in locals():
            all_summaries = {}
            if os.path.exists(output_file_path):
                try:
                    with open(output_file_path, 'r', encoding='utf-8') as f:
                        all_summaries = json.load(f)
                except json.JSONDecodeError:
                    all_summaries = {}

        os.makedirs(os.path.dirname(output_file_path),
                    exist_ok=True)  # Ensure directory exists

        current_summary_details = {
            "summary_content": summary,
            "retrieved_news_count": retrieved_news_count,
            "last_updated": datetime.now().isoformat()
        }
        all_summaries[today_str] = current_summary_details

        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(all_summaries, f, ensure_ascii=False, indent=4)
            show_workflow_status(
                f"{agent_name}: Macro news summary has been saved to: {output_file_path}")
        except Exception as e:
            show_workflow_status(f"{agent_name}: Failed to save macro news summary file: {e}")
            show_agent_reasoning(
                f"Failed to save summary to {output_file_path}: {str(e)}", agent_name)

    show_workflow_status(f"{agent_name}: Execution finished.")

    new_message_content = f"Macro News Agent Analysis for {today_str} (from_cache={from_cache}):\n{summary}"
    new_message = HumanMessage(content=new_message_content, name=agent_name)

    agent_details_for_metadata = {
        "summary_generated_on": today_str,
        "news_count_for_summary": retrieved_news_count,
        "llm_summary_preview": summary[:150] + "..." if len(summary) > 150 else summary,
        "loaded_from_cache": from_cache
    }
    return {
        "messages": [new_message],
        "data": {**state["data"], "macro_news_analysis_result": summary},
        "metadata": {
            **state["metadata"],
            f"{agent_name}_details": agent_details_for_metadata
        }
    }
