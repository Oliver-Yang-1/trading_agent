from typing import Literal

# Define available LLM types
LLMType = Literal["basic", "reasoning", "vision"]

# Define agent-LLM mapping
AGENT_LLM_MAP: dict[str, LLMType] = {
    "coordinator": "basic",  # 协调默认使用basic llm
    "planner": "reasoning",  # 计划默认使用basic llm
    "supervisor": "basic",  # 决策使用basic llm
    "researcher": "basic",  # 简单搜索任务使用basic llm
    "coder": "basic",  # 编程任务使用basic llm
    "reporter": "basic",  # 编写报告使用basic llm
    "data_fetcher": "basic",  # 数据获取使用basic llm
    "algogene_data_fetcher": "basic",  # Algogene数据获取使用basic llm
    "algogene_archieve": "basic",  # Algogene归档使用basic llm
}
