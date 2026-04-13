import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from langgraph_backend import chatbot
import uuid

# utils
def generateThreadId():
    thread_id = uuid.uuid4()
    return thread_id

def resetChat():
    thread_id = generateThreadId()
    st.session_state['thread_id'] = thread_id
    addThread(st.session_state['thread_id'])

    st.session_state['messages'] = []

def addThread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        
def load_messages(thread_id):
    messages = chatbot.get_state(config={'configurable':{"thread_id":thread_id}})
    if "messages" in messages.values:
        messages = [{"role":"user", "content":message.content} if isinstance(message, HumanMessage) else {"role":"assistant", "content":message.content} for message in messages.values['messages']]
        st.session_state['messages'] = messages
        
    else : 
        st.session_state['messages'] = []
        
# store messages in streamlit session
if "messages" not in st.session_state:
    st.session_state['messages'] = []
    
if "thread_id" not in st.session_state:
    st.session_state['thread_id'] = generateThreadId()
    
if "chat_threads" not in st.session_state:
    st.session_state['chat_threads'] = []
    
addThread(st.session_state['thread_id'])


# Side bar
st.sidebar.title("LangGraph Chatbot")
if st.sidebar.button("New Chat"):
    resetChat()
    
st.sidebar.header("My Conversations")
for thread_id in st.session_state['chat_threads']:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        load_messages(thread_id=thread_id)

config = {
    "configurable":{
        "thread_id": st.session_state['thread_id']
    }
}

for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.text(message["content"])

user_query = st.chat_input("type here")

if user_query:
    st.session_state['messages'].append({"role":"user", "content": user_query})
    with st.chat_message("user"):
        st.text(user_query)

    # res = chatbot.invoke({"messages":[HumanMessage(content=user_query)]}, config=config)
    stream = chatbot.stream({'messages':[HumanMessage(content=user_query)]}, config=config, stream_mode="messages")
    
    # print(type(stream))
        
    with st.chat_message("assistant"):
        # we pass chunks in write stream
            ai_response = st.write_stream(message_chunk.content for message_chunk, metadata in stream)
            
    st.session_state['messages'].append({"role":"assistant", "content": ai_response})
    # st.text(st.session_state['messages'][-1]['content'])