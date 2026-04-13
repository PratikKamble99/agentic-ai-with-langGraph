import streamlit as st
from langchain_core.messages import HumanMessage

from langgraph_backend import chatbot

# store messages in streamlit session
if "messages" not in st.session_state:
    st.session_state['messages'] = []

config = {
    "configurable":{
        "thread_id":'1'
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