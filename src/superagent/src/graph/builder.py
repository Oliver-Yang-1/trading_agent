from langgraph.graph import StateGraph, START

from .types import State
from .nodes import (
    supervisor_node,
    research_node,
    code_node,
    coordinator_node,
    data_fetcher_node,
    algogene_data_fetcher_node,
    algogene_archieve_node,
    reporter_node,
    planner_node,
)


def build_graph():
    """Build and return the agent workflow graph."""
    builder = StateGraph(State)
    builder.add_edge(START, "coordinator")
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("planner", planner_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", research_node)
    builder.add_node("coder", code_node)
    builder.add_node("data_fetcher", data_fetcher_node)
    builder.add_node("algogene_data_fetcher", algogene_data_fetcher_node)
    builder.add_node("algogene_archieve", algogene_archieve_node)
    # browser node removed
    builder.add_node("reporter", reporter_node)
    return builder.compile()
