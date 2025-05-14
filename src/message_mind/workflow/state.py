from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


class OutputResponse(BaseModel):
    reasoning: str = Field(description="The reasoning behind the category assignment.")
    summary: str = Field(description="A summary of the message content.")
    category: str = Field(description="The category assigned to the message.")


class AgentState(TypedDict):
    input: dict
    input_id: str
    messages: Annotated[list[AnyMessage], add_messages]
    final_response: OutputResponse
