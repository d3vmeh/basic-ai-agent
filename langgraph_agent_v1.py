import os
import random
from typing import TypedDict, List, Union, Annotated
from langchain_core.messages import BaseMessage
from langchain_core.agents import AgentAction, AgentFinish
from langchain.tools import Tool, tool, BaseTool, StructuredTool
from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.agents import AgentFinish
from langgraph.prebuilt.tool_executor import ToolExecutor
from langgraph.graph import END, StateGraph
import operator




OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

# Setting the agent state -- from LangGraph GitHub
class AgentState(TypedDict):
    #Input string
    input: str
    #List of previous messages
    chat_history: list[BaseMessage]
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

#print(random_number.run('random'))


prompt = hub.pull("hwchase17/openai-functions-agent")
llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)

agent_runnable = create_openai_functions_agent(llm, tools, prompt)


inputs = {"input": "give me a random number and then write it in words and then make it lower case.",
          "chat_history": [],
          "intermediate_steps": []}

agent_outcome = agent_runnable.invoke(inputs)
print(agent_outcome)

tool_executor = ToolExecutor(tools)


def run_agent(data):
    agent_outcome = agent_runnable.invoke(data)
    return {"agent_outcome": agent_outcome}


def execute_tools(data):
    #Function gets the agent outcome as an input

    #the agent outcome becomes the agent action and is a key added in the agent above
    agent_action = data["agent_outcome"]
    output = tool_executor.invoke(agent_action)
    print(f"Agent action: {agent_action}")
    print(f"Tool result: {output}")

    #The output is added to the intermediate steps
    return {"intermediate_steps": [(agent_action, output)]}

#Determining if, based on the preivous outcome, should the agent be done or should it continue
def should_continue(data):
    #If ending, tools don't need to be called and the agent will be finished
    if isinstance(data["agent_outcome"], AgentFinish):
        return "end"
    else:
        return "continue"
    
#Creating a new graph
workflow = StateGraph(AgentState)

#Definiing the two nodes that the agent will cycle between
workflow.add_node("agent", run_agent)
workflow.add_node("action", execute_tools)

workflow.set_entry_point("agent")

# After agent, the conditional edges will be either should continue to end
workflow.add_conditional_edges(
    "agent", should_continue,
    {
        "continue": "action",
        "end": END
    }
)

#Fixed edge from action to agent
#After tools is called, agent node will then be called
workflow.add_edge("action", "agent")
app = workflow.compile()

inputs = {"input": "give me a random number and then write it in words and then make it lower case.","chat_history": []}

output = app.invoke(inputs)

output.get("agent_outcome").return_values["output"]
print(output.get("intermediate_steps"))




