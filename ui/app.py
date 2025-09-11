import streamlit as st
import requests

API_URL = "http://localhost:8000"  # your FastAPI server

st.set_page_config(page_title="Student Document QA", layout="wide")

st.title("📘 Student Document QA System")

# Sidebar - document upload
st.sidebar.header("📂 Upload Documents")
uploaded_file = st.sidebar.file_uploader("Upload a document (PDF/TXT)", type=["pdf", "txt"])

if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
    response = requests.post(f"{API_URL}/upload", files=files)
    if response.status_code == 200:
        st.sidebar.success("✅ Document uploaded and processed!")
    else:
        st.sidebar.error("❌ Upload failed. Check backend logs.")

# Main chat area
st.subheader("💬 Ask Questions About Your Documents")
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Show history
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your question..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    print(prompt)

    response = requests.post(f"{API_URL}/chat", json={"query": prompt})
    print(response)
    if response.status_code == 200:
        answer = response.json().get("answer", "No response")
    else:
        answer = "Error: could not reach backend."

    st.session_state["messages"].append({"role": "assistant", "content": answer})
    st.chat_message("assistant").markdown(answer)
