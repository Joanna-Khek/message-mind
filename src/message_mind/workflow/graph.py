from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from langgraph.prebuilt import ToolNode

from message_mind.workflow.state import AgentState
from message_mind.workflow import nodes, tools


def create_workflow_graph():
    graph_builder = StateGraph(AgentState)

    # Add all nodes
    graph_builder.add_node("agent", nodes.call_model)
    graph_builder.add_node("respond", nodes.respond)
    graph_builder.add_node("tools", ToolNode(tools.tools))

    # Define workflow
    graph_builder.add_edge(START, "agent")
    graph_builder.add_conditional_edges(
        "agent",
        nodes.should_continue,
        {"continue": "tools", "respond": "respond"},
    )
    graph_builder.add_edge("tools", "agent")
    graph_builder.add_edge("respond", END)

    graph = graph_builder.compile(checkpointer=MemorySaver())

    return graph
