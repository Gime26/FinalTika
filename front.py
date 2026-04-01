import streamlit as st
from tikabot import predict_class, get_response, intents
import os , pathlib

st.title("TikaBot")

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensaje de bienvenida fijo
    st.session_state.messages.append({"role": "assistant", "content": "Hola, ¿cómo puedo ayudarte?"})

for message in st.session_state.messages:
    content= message.get("content","")
    if content:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


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

    
