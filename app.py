import streamlit as st
from src.agent import run_agent

st.set_page_config(
    page_title="NBA AI Agent",
    page_icon="🏀",
    layout="centered"
)

st.title("🏀 NBA AI Agent")
st.caption("Ask me anything about NBA stats, teams, and predictions")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []

# Suggested questions – prikaži samo ako nema poruka
if not st.session_state.messages:
    st.markdown("#### Try asking:")
    
    suggested = [
        "🏆 Which team has the most wins?",
        "🔮 Who would win, Thunder or Celtics?",
        "📊 What are LeBron James' stats?",
        "⚔️ Compare LeBron James and Stephen Curry",
        "🌍 Show me the full NBA standings",
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(suggested):
        with cols[i % 2]:
            if st.button(question, use_container_width=True):
                st.session_state.pending_question = question
                st.rerun()

# Handle suggested question click
if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response, st.session_state.history = run_agent(prompt, st.session_state.history)
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Prikaži historiju
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("E.g. Who has the most wins? Compare LeBron and Curry"):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response, st.session_state.history = run_agent(prompt, st.session_state.history)
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})