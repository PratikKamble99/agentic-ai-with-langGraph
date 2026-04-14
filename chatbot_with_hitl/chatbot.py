# import deps
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated , List, Any, Literal
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, AnyMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver 

from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.types import interrupt, Command

from dotenv import load_dotenv

load_dotenv()

# create llm
llm = ChatOpenAI(model="gpt-4.1-mini")
checkpointer = MemorySaver()

#create graph state
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
# create tools
searchTool = DuckDuckGoSearchRun(region='us-en')

@tool
def buy_shares(stock: str, quantity: int) -> str:
    """
    You are an tool which buys shares on behalf of user

    Args:
        stock (str): stock name
        quantity (int): quantity of shares to buy

    Returns:
        str: purchase confirmation message
    """
    print(f"Request to buy {quantity} shares of {stock} received. Awaiting human approval...")
    decision = interrupt(f"Approve buying {quantity} shares of {stock}? (yes/no)")
    
    if isinstance(decision, str) and decision.lower() == "yes":
        return {
            "status": "success",
            "message": f"Purchase order placed for {quantity} shares of {stock}.",
            "stock": stock,
            "quantity": quantity,
        }
    
    else:
        return {
            "status": "cancelled",
            "message": f"Purchase of {quantity} shares of {stock} was declined by human.",
            "stock": stock,
            "quantity": quantity,
        }

tools = [searchTool, buy_shares]

llm_with_tools = llm.bind_tools(tools)

# build graph
graph = StateGraph(State)

# create node and edges
tool_node = ToolNode(tools=tools)

def chat_node(state: State):
    """ call tool based on user query"""
    response = llm_with_tools.invoke( state["messages"])
    return {"messages": [response]}

graph.add_node("tools", tool_node)
graph.add_node("chat", chat_node)

graph.add_edge(START, "chat")
graph.add_conditional_edges("chat", tools_condition)
graph.add_edge("tools", "chat")

#compile graph
workflow = graph.compile(checkpointer=checkpointer)

config = {"configurable":{'thread_id': '1234'}}

while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting chat...")
        break
    
    res = workflow.invoke({'messages':[HumanMessage(user_input)]}, config=config)
    interrupt_data = res.get("__interrupt__")
    
    if interrupt_data:
        print("Graph paused for human approval..")
        message = interrupt_data[0].value

        # ── Step 2: simulate the human decision ──────────────────────────────────
        human_decision = input(f"Enter your decision (yes/no): ")
        
        print(f"Human decision: {human_decision}")

        # Resume the graph by passing Command(resume=...) instead of a new input.
        final_result = workflow.invoke(Command(resume=human_decision), config=config)
        
       
        for msg in final_result["messages"][-2:]:  # print the last 2 messages in the conversation
            print(f"  [{type(msg).__name__}]: {msg.content}")
    else:
        print("Graph completed without interruption:")
        for msg in res["messages"][-2:]:
            print(f"  [{type(msg).__name__}]: {msg.content}")


