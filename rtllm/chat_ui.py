import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="RedTeam LLM", page_icon="🛡️")
st.title("💬 RedTeam LLM Chat")

if "history" not in st.session_state:
    st.session_state["history"] = []

# Input box
user_input = st.chat_input("Type your message here...")

if user_input:
    # Call your FastAPI backend
    response = requests.post(API_URL, json={"prompt": user_input})
    data = response.json()
    answer = data.get("response", "[Error: No response]")

    # Save to chat history
    st.session_state["history"].append(("user", user_input))
    st.session_state["history"].append(("assistant", answer))

# Render chat history
for role, msg in st.session_state["history"]:
    if role == "user":
        st.chat_message("user").write(msg)
    else:
        st.chat_message("assistant").write(msg)
