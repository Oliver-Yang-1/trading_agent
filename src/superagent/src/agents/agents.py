from langgraph.prebuilt import create_react_agent

from src.prompts import apply_prompt_template,apply_prompt_template_compressed
from src.tools import (
    bash_tool,
    crawl_tool,
    python_repl_tool,
    tavily_tool,
    get_financial_metrics,
    get_market_data,
    get_price_history,
    get_financial_statements,
    algogene_docs_reader_tool,
    algogene_code_generator_tool,
)

# Import Algogene client functions
from src.tools.algogene_client import (
    get_algogene_price_history,
    check_valid_instrument,
    search_instrument_with_prefix,
)

from .llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP

# Create agents using configured LLM types
research_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["researcher"]),
    tools=[tavily_tool, crawl_tool],
    prompt=lambda state: apply_prompt_template_compressed("researcher", state),
)

coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["coder"]),
    tools=[python_repl_tool, bash_tool],
    prompt=lambda state: apply_prompt_template_compressed("coder", state),
)

data_fetcher_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["data_fetcher"]),
    tools=[
        get_financial_metrics,
        get_market_data,
        get_price_history,
        get_financial_statements,
    ],
    prompt=lambda state: apply_prompt_template_compressed("data_fetcher", state),
)

algogene_data_fetcher_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["algogene_data_fetcher"]),
    tools=[
        get_algogene_price_history,
        check_valid_instrument,
        search_instrument_with_prefix,
    ],
    prompt=lambda state: apply_prompt_template_compressed("algogene_data_fetcher", state),
)

algogene_archieve_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["algogene_archieve"]),
    tools=[algogene_docs_reader_tool, algogene_code_generator_tool],
    prompt=lambda state: apply_prompt_template_compressed("algogene_archieve", state),
)


