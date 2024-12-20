import os
import random
from typing import TypedDict, List, Union, Annotated
from langchain_core.messages import BaseMessage
from langchain_core.agents import AgentAction, AgentFinish
from langchain.tools import Tool, tool, BaseTool, StructuredTool

import operator

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

# Setting the agent state -- from LangGraph GitHub
class AgentState:
    #Input string
    input: str
    #List of previous messages
    chat_history: List[BaseMessage]
    #Outcome of a given call to the agent, needs "None" to start 
    agent_outcome: Union[AgentAction, AgentFinish, None]
    #List of actions and corresponding observations
    #Annotated using operator.add to show that operations/edits to this state should be added to the existing values rather than overwriting them
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


#Making custom tools used in tutorial
@tool("lower_case", return_direct=True)
def lower_case(text: str) -> str:
    """Return the input text in all lowercase"""
    return text.lower()

@tool("random", return_direct=True)
def random_number(text: str) -> str:
    """Return a random number between 0 and 100"""
    return str(random.randint(0, 100))


#Setting tools for agent to use
tools = [lower_case, random_number]

print(random_number.run('random'))
