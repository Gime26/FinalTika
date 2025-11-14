import streamlit as st
from tikabot import predict_class, get_response, intents

with open('tikabot.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
st.title("TikaBot")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "first_message" not in st.session_state:
    st.session_state.first_message = True 

for message in st.session_state.messages:
    content= message.get("content","")
    if content:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if st.session_state.first_message:
    initial_message = "Hola, ¿cómo puedo ayudarte?"
    
    with st.chat_message("assistant"):
        st.markdown(initial_message)
    #st.session_state.messages.append({"role":"assistant","content":initial_message})
    st.session_state.first_message = False

if prompt := st.chat_input("¿cómo puedo ayudarte?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role":"user","content": prompt}) 

    #Implementación de IA
    insts = predict_class(prompt)
    res = get_response(insts, intents)
    with st.chat_message("assistant"):
        st.markdown(res)

    st.session_state.messages.append({"role":"assistant","content": res})