import os
import json
from datetime import datetime
import akshare as ak
from src.utils.logging_config import setup_logger
from src.agents.state import AgentState, show_agent_reasoning, show_workflow_status
from typing import Dict, Any, List
from src.utils.api_utils import agent_endpoint
from src.tools.openrouter_config import get_chat_completion
from langchain_core.messages import HumanMessage
import re

# LLM Prompt for analyzing full news data
LLM_PROMPT_MACRO_ANALYSIS = """You are a senior macro analyst specializing in the A-share (China) market.

Based on the CSI 300 Index news data provided below, analyze the market and return ONLY a valid JSON object with these exact fields:

- overall_sentiment: "bullish", "bearish", or "neutral"
- sentiment_confidence: number between 0.0 and 1.0
- key_hot_sectors_or_themes: array of 1-3 strings
- key_potential_risks: array of 1-2 strings  
- policy_impact_summary: string (if no significant policy news, use "No significant policy news identified")
- market_outlook_short_term: string (outlook for next few trading days)
- detailed_analysis_report: string (comprehensive analysis covering market sentiment, hot sectors, risks, policy impacts, and outlook)

IMPORTANT: 
- Return ONLY the JSON object, no other text
- Do not use markdown code blocks
- Ensure all text content is in English
- For the detailed_analysis_report field, write as a single continuous text without line breaks

CSI 300 News Data:
{news_data_json_string}

JSON Response:"""

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
    parsed_summary: Dict[str, Any] = {}
    summary_json_str: str = ""
    retrieved_news_count = 0
    from_cache = False

    today_str = datetime.now().strftime("%Y-%m-%d")
    output_file_path = os.path.join("src", "data", "macro_summary.json")

    # Default JSON structure for errors or no data
    default_error_json = {
        "overall_sentiment": "neutral",
        "sentiment_confidence": 0.0,
        "key_hot_sectors_or_themes": [],
        "key_potential_risks": ["Analysis error or no data"],
        "policy_impact_summary": "Unavailable",
        "market_outlook_short_term": "Unavailable",
        "detailed_analysis_report": "Macro analysis could not be performed."
    }

    # Attempt to load from cache first
    if os.path.exists(output_file_path):
        try:
            with open(output_file_path, 'r', encoding='utf-8') as f:
                all_summaries = json.load(f)
            if today_str in all_summaries and all_summaries[today_str]:
                cached_data = all_summaries[today_str]
                
                # Check if new format exists (parsed_summary field)
                if "parsed_summary" in cached_data and isinstance(cached_data["parsed_summary"], dict):
                    parsed_summary = cached_data["parsed_summary"]
                    summary_json_str = cached_data.get("summary_json_str", json.dumps(parsed_summary, ensure_ascii=False))
                    from_cache = True
                    show_workflow_status(f"{agent_name}: Loaded new format macro news summary for {today_str} from cache.")
                
                # Handle old format (summary_content field)
                elif "summary_content" in cached_data:
                    old_content = cached_data["summary_content"]
                    if isinstance(old_content, str):
                        try:
                            # Try to parse as JSON
                            parsed_summary = json.loads(old_content)
                            summary_json_str = old_content
                            if "detailed_analysis_report" not in parsed_summary:
                                # Old plain text or different JSON format
                                parsed_summary = {
                                    **default_error_json,
                                    "detailed_analysis_report": f"Legacy cached summary: {old_content}",
                                    "overall_sentiment": "neutral",
                                }
                                summary_json_str = json.dumps(parsed_summary, ensure_ascii=False)
                        except json.JSONDecodeError:
                            # Old plain text format
                            parsed_summary = {
                                **default_error_json,
                                "detailed_analysis_report": f"Legacy cached summary: {old_content}",
                                "overall_sentiment": "neutral",
                            }
                            summary_json_str = json.dumps(parsed_summary, ensure_ascii=False)
                    elif isinstance(old_content, dict):
                         parsed_summary = old_content
                         summary_json_str = json.dumps(parsed_summary, ensure_ascii=False)
                    else:
                        parsed_summary = {**default_error_json, "detailed_analysis_report": "Unknown legacy cache format."}
                        summary_json_str = json.dumps(parsed_summary, ensure_ascii=False)
                    from_cache = True
                    show_workflow_status(f"{agent_name}: Loaded and converted old format macro news summary for {today_str} from cache.")
                
                if from_cache:
                    retrieved_news_count = cached_data.get("retrieved_news_count", 0)
                    show_agent_reasoning(f"Loaded macro summary for {today_str} from cache. News count: {retrieved_news_count}", agent_name)

        except (json.JSONDecodeError, Exception) as e:
            show_agent_reasoning(f"Error loading cache from {output_file_path}: {str(e)}. Will fetch fresh data.", agent_name)
            all_summaries = {}

    if not from_cache:
        show_workflow_status(f"{agent_name}: No summary found in cache for today, fetching real-time news.")
        try:
            show_workflow_status(f"{agent_name}: Fetching news for symbol {symbol}")
            news_df = ak.stock_news_em(symbol=symbol)
            
            if news_df is None or news_df.empty:
                show_workflow_status(f"{agent_name}: No news data retrieved for {symbol}.")
                show_agent_reasoning(f"No news found for {symbol}. Proceeding with no data summary.", agent_name)
                parsed_summary = {**default_error_json, "detailed_analysis_report": "No macro news data available today."}
                summary_json_str = json.dumps(parsed_summary, ensure_ascii=False)
            else:
                retrieved_news_count = len(news_df)
                show_workflow_status(f"{agent_name}: Successfully retrieved {retrieved_news_count} news items for {symbol}.")
                show_agent_reasoning(f"Successfully fetched {retrieved_news_count} news items for {symbol}. Preparing for LLM analysis.", agent_name)
                
                for _, row in news_df.iterrows():
                    news_item = {
                        "title": str(row.get("新闻标题", "")).strip(),
                        "content": str(row.get("新闻内容", "")).strip(),
                        "publish_time": str(row.get("发布时间", "")).strip()
                    }
                    news_list_for_llm.append(news_item)

                news_data_json_string_for_prompt = json.dumps(news_list_for_llm, ensure_ascii=False, indent=2)
                prompt_filled = LLM_PROMPT_MACRO_ANALYSIS.format(news_data_json_string=news_data_json_string_for_prompt)

                show_workflow_status(f"{agent_name}: Calling LLM for analysis.")
                llm_response_str = get_chat_completion(messages=[{"role": "user", "content": prompt_filled}])

                if llm_response_str:
                    llm_response_clean = llm_response_str.strip()
                    
                    # Extract JSON from LLM response
                    json_match = re.search(r"\{.*\}", llm_response_clean, re.DOTALL)
                    if json_match:
                        extracted_json_str_raw = json_match.group(0)

                        try:
                            # Try direct parsing first
                            parsed_summary = json.loads(extracted_json_str_raw)
                            summary_json_str = extracted_json_str_raw
                        except json.JSONDecodeError:
                            # Apply fixes if direct parsing fails
                            extracted_json_str_stripped = extracted_json_str_raw.strip()
                            
                            # Remove outer quotes if present
                            if (extracted_json_str_stripped.startswith("'") and extracted_json_str_stripped.endswith("'")) or \
                               (extracted_json_str_stripped.startswith('"') and extracted_json_str_stripped.endswith('"')):
                                extracted_json_str_stripped = extracted_json_str_stripped[1:-1]
                            
                            # Fix escaped single quotes
                            if "\\'" in extracted_json_str_stripped:
                                extracted_json_str_stripped = extracted_json_str_stripped.replace("\\'", "'")
                            
                            try:
                                parsed_summary = json.loads(extracted_json_str_stripped)
                                summary_json_str = extracted_json_str_stripped
                            except json.JSONDecodeError as je2:
                                logger.error(f"All parsing attempts failed: {je2}")
                                parsed_summary = {**default_error_json, "detailed_analysis_report": f"JSON parsing failed: {str(je2)}"}
                                summary_json_str = json.dumps(parsed_summary, ensure_ascii=False)
                    else:
                        logger.error(f"Could not find JSON object in LLM response")
                        parsed_summary = {**default_error_json, "detailed_analysis_report": "No JSON object found in LLM response"}
                        summary_json_str = json.dumps(parsed_summary, ensure_ascii=False)
                else:
                    logger.error(f"{agent_name}: LLM analysis failed to return any response.")
                    parsed_summary = {**default_error_json, "detailed_analysis_report": "LLM analysis failed to return valid results."}
                    summary_json_str = json.dumps(parsed_summary, ensure_ascii=False)
                
                show_workflow_status(f"{agent_name}: LLM macro analysis result obtained.")
                show_agent_reasoning(f"LLM analysis complete. JSON (first 100 chars): {summary_json_str[:100]}...", agent_name)

        except Exception as e:
            show_workflow_status(f"{agent_name}: Exception occurred during news fetching or LLM call: {e}")
            show_agent_reasoning(f"Exception during execution: {str(e)}", agent_name)
            parsed_summary = {**default_error_json, "detailed_analysis_report": f"An error occurred: {str(e)}"}
            summary_json_str = json.dumps(parsed_summary, ensure_ascii=False)

    # Ensure data is populated
    if not parsed_summary:
        parsed_summary = {**default_error_json, "detailed_analysis_report": "Fell through all logic, using default error."}
    if not summary_json_str:
        summary_json_str = json.dumps(parsed_summary, ensure_ascii=False)

    # Save summary to JSON file
    if not from_cache or not os.path.exists(output_file_path):
        show_workflow_status(f"{agent_name}: Preparing to save summary to {output_file_path}")

        if 'all_summaries' not in locals():
            all_summaries = {}
            if os.path.exists(output_file_path):
                try:
                    with open(output_file_path, 'r', encoding='utf-8') as f:
                        all_summaries = json.load(f)
                except json.JSONDecodeError:
                    all_summaries = {}

        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        current_summary_details_to_save = {
            "parsed_summary": parsed_summary,
            "summary_json_str": summary_json_str,
            "retrieved_news_count": retrieved_news_count,
            "last_updated": datetime.now().isoformat()
        }
        all_summaries[today_str] = current_summary_details_to_save

        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(all_summaries, f, ensure_ascii=False, indent=4)
            show_workflow_status(f"{agent_name}: Macro news summary has been saved to: {output_file_path}")
        except Exception as e:
            show_workflow_status(f"{agent_name}: Failed to save macro news summary file: {e}")
            show_agent_reasoning(f"Failed to save summary to {output_file_path}: {str(e)}", agent_name)

    show_workflow_status(f"{agent_name}: Execution finished.")

    new_message = HumanMessage(content=summary_json_str, name=agent_name)

    agent_details_for_metadata = {
        "summary_generated_on": today_str,
        "news_count_for_summary": retrieved_news_count,
        "llm_summary_preview": summary_json_str[:150] + "..." if len(summary_json_str) > 150 else summary_json_str,
        "loaded_from_cache": from_cache,
        "overall_sentiment_from_json": parsed_summary.get("overall_sentiment", "N/A")
    }
    
    return {
        "messages": [new_message],
        "data": {**state["data"], "macro_news_analysis_result": parsed_summary},
        "metadata": {
            **state["metadata"],
            f"{agent_name}_details": agent_details_for_metadata
        }
    }
