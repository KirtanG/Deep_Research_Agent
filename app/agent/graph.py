from langgraph.graph import END, START, StateGraph

from app.agent.configuration import Configuration
from app.agent.nodes import (
    continue_to_web_research,
    evaluate_research,
    finalise_answer,
    generate_query,
    reflection,
    web_research,
)
from app.agent.state import OverallState

builder = StateGraph(state_schema=OverallState,context_schema = Configuration)

# Define the nodes we will cycle between
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalise_answer)

# Set the entrypoint as `generate_query`
# This means that this node is the first one called
builder.add_edge(START, "generate_query")
# Add conditional edge to continue with search queries in a parallel branch
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
# Reflect on the web research
builder.add_edge("web_research", "reflection")
# Evaluate the research
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
# Finalize the answer
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="deep-search-agent")
