import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"
user_id = "demo_user"

st.set_page_config(layout="wide")

# =========================
# SESSION STATE INIT
# =========================
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "threads" not in st.session_state:
    st.session_state.threads = []

if "documents" not in st.session_state:
    st.session_state.documents = []


# =========================
# BACKEND FETCH FUNCTIONS
# =========================

def fetch_threads():
    try:
        response = requests.get(
            f"{API_URL}/list-threads",
            params={"user_id": user_id}
        )
        if response.status_code == 200:
            return response.json()["threads"]
    except:
        pass
    return []


def fetch_documents(thread_id):
    try:
        response = requests.get(
            f"{API_URL}/list-documents",
            params={
                "user_id": user_id,
                "thread_id": thread_id
            }
        )
        if response.status_code == 200:
            return response.json()["documents"]
    except:
        pass
    return []


def fetch_messages(thread_id):
    try:
        response = requests.get(
            f"{API_URL}/get-thread",
            params={
                "user_id": user_id,
                "thread_id": thread_id
            }
        )
        if response.status_code == 200:
            return response.json()["messages"]
    except:
        pass
    return []


# =========================
# INITIAL LOAD
# =========================
if st.session_state.thread_id is None:

    threads = fetch_threads()

    if not threads:
        st.session_state.thread_id = "thread_1"
    else:
        st.session_state.thread_id = threads[0]

    st.session_state.threads = threads
    st.session_state.messages = fetch_messages(st.session_state.thread_id)
    st.session_state.documents = fetch_documents(st.session_state.thread_id)


# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.title("📂 Workspace")

    # ---------------------
    # New Conversation
    # ---------------------
    if st.button("➕ New Conversation"):
        new_thread = f"thread_{len(fetch_threads()) + 1}"

        st.session_state.thread_id = new_thread
        st.session_state.messages = []

        # Create thread in backend
        requests.post(
            f"{API_URL}/ask",
            params={
                "user_id": user_id,
                "thread_id": new_thread,
                "question": "Start conversation"
            }
        )

        st.rerun()

    st.divider()

    # ---------------------
    # THREAD LIST
    # ---------------------
    st.subheader("💬 Conversations")

    threads = fetch_threads()

    for thread in threads:
        if st.button(thread):
            st.session_state.thread_id = thread
            st.session_state.messages = fetch_messages(thread)
            st.session_state.documents = fetch_documents(thread)
            st.rerun()

    st.divider()

    # ---------------------
    # Upload PDF (THREAD SCOPED)
    # ---------------------
    st.subheader("📁 Upload Document")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:

        files = {"file": uploaded_file}

        response = requests.post(
            f"{API_URL}/upload",
            params={
                "user_id": user_id,
                "thread_id": st.session_state.thread_id   # 🔥 IMPORTANT FIX
            },
            files=files
        )

        if response.status_code == 200:
            st.success("Uploaded successfully")
            st.session_state.documents = fetch_documents(st.session_state.thread_id)
        else:
            st.error(response.text)

    st.divider()

    # ---------------------
    # DOCUMENT LIST (THREAD BASED)
    # ---------------------
    st.subheader("📄 Documents")

    documents = fetch_documents(st.session_state.thread_id)

    selected_doc = st.selectbox(
        "Select document (optional)",
        ["None"] + documents
    )

    doc_id = None if selected_doc == "None" else selected_doc


# =========================
# MAIN CHAT
# =========================
st.title("🤖 Multilingual RAG Assistant")

st.caption(f"Active Thread: {st.session_state.thread_id}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# =========================
# CHAT INPUT
# =========================
user_input = st.chat_input("Ask anything...")

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            response = requests.post(
                f"{API_URL}/ask",
                params={
                    "user_id": user_id,
                    "thread_id": st.session_state.thread_id,
                    "question": user_input,
                    "doc_id": doc_id
                }
            )

            if response.status_code == 200:
                answer = response.json()["answer"]
            else:
                answer = response.text

            st.write(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })