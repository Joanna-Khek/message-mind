import os
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI

from message_mind.workflow.state import AgentState, OutputResponse
from message_mind.workflow import tools, prompts

llm = ChatOpenAI(
    model="gpt-4o-mini", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY")
)

llm_with_structured_output = llm.with_structured_output(OutputResponse)
llm_with_tools = llm.bind_tools(tools.tools)


def call_model(state: AgentState):
    system_msg = SystemMessage(content=prompts.agent_system_prompt)

    user_msg = HumanMessage(
        content=prompts.user_prompt.format(
            message=state["input"], unique_categories=state["unique_categories"]
        )
    )

    response = llm_with_tools.invoke([system_msg, user_msg] + state["messages"])
    return {"messages": [response]}  # Add to existing list


def respond(state: AgentState):
    """
    Takes the final answer from the model and format into a structured output
    """
    for msg in reversed(state["messages"]):
        if isinstance(msg, AIMessage) and not getattr(msg, "tool_calls", None):
            final_content = msg.content
            break
        else:
            final_content = state["messages"][-1].content

    response = llm_with_structured_output.invoke([HumanMessage(content=final_content)])
    return {"final_response": response}


def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    # If there is no function call, then we respond to the user
    if not last_message.tool_calls:
        return "respond"
    else:
        return "continue"
