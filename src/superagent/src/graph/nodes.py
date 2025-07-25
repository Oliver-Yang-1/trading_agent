import logging
import json
from copy import deepcopy
from typing import Literal
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from langgraph.graph import END

from src.agents import research_agent, coder_agent, data_fetcher_agent, algogene_data_fetcher_agent, algogene_archieve_agent
from src.agents.llm import get_llm_by_type
from src.config import TEAM_MEMBERS
from src.config.agents import AGENT_LLM_MAP
from src.prompts.template import apply_prompt_template
from src.tools.search import tavily_tool
from src.tools.report_saver import save_report_to_markdown
from .types import State, Router

logger = logging.getLogger(__name__)

RESPONSE_FORMAT = "Response from {}:\n\n<response>\n{}\n</response>\n\n*Please execute the next step.*"


def research_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the researcher agent that performs research tasks."""
    logger.info("Research agent starting task")
    result = research_agent.invoke(state)
    logger.info("Research agent completed task")
    logger.debug(f"Research agent response: {result['messages'][-1].content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "researcher", result["messages"][-1].content
                    ),
                    name="researcher",
                )
            ]
        },
        goto="supervisor",
    )


def code_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the coder agent that executes Python code."""
    logger.info("Code agent starting task")
    result = coder_agent.invoke(state,{"recursion_limit":9999})
    logger.info("Code agent completed task")
    logger.debug(f"Code agent response: {result['messages'][-1].content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "coder", result["messages"][-1].content
                    ),
                    name="coder",
                )
            ]
        },
        goto="supervisor",
    )


def data_fetcher_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the data fetcher agent that performs data fetching tasks."""
    logger.info("Data fetcher agent starting task")
    result = data_fetcher_agent.invoke(state,{"recursion_limit":9999})
    logger.info("Data fetcher agent completed task")
    logger.debug(f"Data fetcher agent response: {result['messages'][-1].content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "data_fetcher", result["messages"][-1].content
                    ),
                    name="data_fetcher",
                )
            ]
        },
        goto="supervisor",
    )


# def browser_node(state: State) -> Command[Literal["supervisor"]]:
#     """Node for the browser agent that performs web browsing tasks."""
#     logger.info("Browser agent starting task")
#     result = browser_agent.invoke(state)
#     logger.info("Browser agent completed task")
#     logger.debug(f"Browser agent response: {result['messages'][-1].content}")
#     return Command(
#         update={
#             "messages": [
#                 HumanMessage(
#                     content=RESPONSE_FORMAT.format(
#                         "browser", result["messages"][-1].content
#                     ),
#                     name="browser",
#                 )
#             ]
#         },
#         goto="supervisor",
#     )


def supervisor_node(state: State) -> Command[Literal[*TEAM_MEMBERS, "__end__"]]:
    """Supervisor node that decides which agent should act next."""
    logger.info("Supervisor evaluating next action")
    messages = apply_prompt_template("supervisor", state)
    response = (
        get_llm_by_type(AGENT_LLM_MAP["supervisor"])
        .with_structured_output(Router)
        .invoke(messages)
    )
    goto = response["next"]
    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"Supervisor response: {response}")

    if goto == "FINISH":
        goto = "__end__"
        logger.info("Workflow completed")
    else:
        logger.info(f"Supervisor delegating to: {goto}")

    return Command(goto=goto, update={"next": goto})


def planner_node(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """Planner node that generate the full plan."""
    logger.info("Planner generating full plan")
    messages = apply_prompt_template("planner", state)
    # whether to enable deep thinking mode
    llm = get_llm_by_type("basic")
    if state.get("deep_thinking_mode"):
        llm = get_llm_by_type("reasoning")
    if state.get("search_before_planning"):
        searched_content = tavily_tool.invoke({"query": state["messages"][-1].content})
        messages = deepcopy(messages)
        messages[
            -1
        ].content += f"\n\n# Relative Search Results\n\n{json.dumps([{'titile': elem['title'], 'content': elem['content']} for elem in searched_content], ensure_ascii=False)}"
    stream = llm.stream(messages)
    full_response = ""
    for chunk in stream:
        full_response += chunk.content
    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"Planner response: {full_response}")

    if full_response.startswith("```json"):
        full_response = full_response.removeprefix("```json")

    if full_response.endswith("```"):
        full_response = full_response.removesuffix("```")

    goto = "supervisor"
    try:
        json.loads(full_response)
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        goto = "__end__"

    return Command(
        update={
            "messages": [HumanMessage(content=full_response, name="planner")],
            "full_plan": full_response,
        },
        goto=goto,
    )


def coordinator_node(state: State) -> Command[Literal["planner", "__end__"]]:
    """Coordinator node that communicate with customers."""
    logger.info("Coordinator talking.")
    messages = apply_prompt_template("coordinator", state)
    response = get_llm_by_type(AGENT_LLM_MAP["coordinator"]).invoke(messages)
    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"reporter response: {response}")

    goto = "__end__"
    if "handoff_to_planner" in response.content:
        goto = "planner"

    return Command(
        goto=goto,
    )


def algogene_data_fetcher_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the algogene data fetcher agent that performs Algogene data fetching tasks."""
    logger.info("Algogene data fetcher agent starting task")
    result = algogene_data_fetcher_agent.invoke(state, {"recursion_limit": 9999})
    logger.info("Algogene data fetcher agent completed task")
    logger.debug(f"Algogene data fetcher agent response: {result['messages'][-1].content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "algogene_data_fetcher", result["messages"][-1].content
                    ),
                    name="algogene_data_fetcher",
                )
            ]
        },
        goto="supervisor",
    )


def algogene_archieve_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the algogene archieve agent that performs data archiving tasks."""
    logger.info("Algogene archieve agent starting task")
    result = algogene_archieve_agent.invoke(state, {"recursion_limit": 9999})
    logger.info("Algogene archieve agent completed task")
    logger.debug(f"Algogene archieve agent response: {result['messages'][-1].content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "algogene_archieve", result["messages"][-1].content
                    ),
                    name="algogene_archieve",
                )
            ]
        },
        goto="supervisor",
    )


def reporter_node(state: State) -> Command[Literal["supervisor"]]:
    """Reporter node that write a final report."""
    logger.info("Reporter write final report")
    messages = apply_prompt_template("reporter", state)
    response = get_llm_by_type(AGENT_LLM_MAP["reporter"]).invoke(messages)
    logger.debug(f"Current state messages: {state['messages']}")
    logger.debug(f"reporter response: {response}")
    
    # Save the report to markdown file
    try:
        saved_path = save_report_to_markdown(response.content)
        logger.info(f"Report saved to: {saved_path}")
    except Exception as e:
        logger.error(f"Failed to save report: {e}")

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format("reporter", response.content),
                    name="reporter",
                )
            ]
        },
        goto="supervisor",
    )
