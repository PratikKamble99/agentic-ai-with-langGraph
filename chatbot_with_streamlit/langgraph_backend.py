from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver 
from langgraph.graph.message import add_messages

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI()
checkpointer = MemorySaver()

    
class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    
graph = StateGraph(State)

def chat(state:State):
    res = llm.invoke(state['messages'])

    return {"messages":[res]}

graph.add_node("chat", chat)

graph.add_edge(START, 'chat')
graph.add_edge("chat", END)

chatbot = graph.compile(checkpointer=checkpointer)