import streamlit as st
import requests
import uuid
import re

# -----------------------------
# PASSWORD PROTECTION
# -----------------------------
PASSWORD = "HoliyaAI"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Access Required")
    password_input = st.text_input("Enter password", type="password")
    if password_input == PASSWORD:
        st.session_state.authenticated = True
        st.success("Access granted ✅")
        st.rerun()
    elif password_input:
        st.error("Incorrect password ❌")
    st.stop()

# -----------------------------
# CONFIG
# -----------------------------
BASE_URL = "http://13.61.194.44/api/chatbot"
USER_ID = 35

st.set_page_config(
    page_title="Holiya Medical AI Agent",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# HOLIYA THEME STYLES
# -----------------------------
st.markdown("""
<style>

/* ---------- APP BACKGROUND ---------- */
.main, .stApp {
    background-color: #F7F3EF;
    color: #3E3A37;
    font-family: 'Inter', sans-serif;
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background-color: #EFE9E4;
}

/* ---------- USER MESSAGE ---------- */
.user-message {
    background-color: #E7EFEA;
    padding: 16px 20px;
    border-radius: 18px;
    margin: 14px 0;
    border-left: 5px solid #8A9A5B;
    color: #3E3A37;
}

/* ---------- AI MESSAGE ---------- */
.ai-message {
    background-color: #FFFFFF;
    padding: 18px 22px;
    border-radius: 18px;
    margin: 14px 0;
    border-left: 5px solid #8A9A5B;
    color: #3E3A37;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

/* ---------- CONTENT BLOCKS ---------- */
.block-info {
    background-color: #EEF3F6;
    padding: 14px 18px;
    border-radius: 14px;
    margin: 12px 0;
    border-left: 4px solid #A3B6C4;
}

.block-success {
    background-color: #E4EFE6;
    padding: 14px 18px;
    border-radius: 14px;
    margin: 12px 0;
    border-left: 4px solid #8A9A5B;
}

.block-warning {
    background-color: #F8EEE6;
    padding: 14px 18px;
    border-radius: 14px;
    margin: 12px 0;
    border-left: 4px solid #C8A27A;
}

.block-danger {
    background-color: #F6E6E6;
    padding: 14px 18px;
    border-radius: 14px;
    margin: 12px 0;
    border-left: 4px solid #C28B8B;
}

/* ---------- HEADINGS ---------- */
.ai-message h1,
.ai-message h2,
.ai-message h3 {
    color: #3E3A37;
    font-weight: 700;
}

/* ---------- TYPOGRAPHY ---------- */
p, li {
    line-height: 1.75;
    color: #3E3A37;
}

ul {
    padding-left: 20px;
}

/* ---------- INLINE HIGHLIGHTS ---------- */
.highlight {
    padding: 4px 8px;
    border-radius: 6px;
    font-weight: 600;
}

.highlight-green {
    background-color: #DDE8DF;
}

.highlight-orange {
    background-color: #F3E2D3;
}

.highlight-red {
    background-color: #EED6D6;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def is_html(text):
    return bool(re.search(r'<[^>]+>', text))

def markdown_to_html(text):
    if not text:
        return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'^### (.*)', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*)', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*)', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    return text.replace("\n", "<br>")

def render_message(text):
    return text if is_html(text) else markdown_to_html(text)

# -----------------------------
# API FUNCTIONS
# -----------------------------
def get_sessions():
    try:
        return requests.get(
            f"{BASE_URL}/get-sessions?user_id={USER_ID}"
        ).json().get("data", [])
    except:
        return []

def get_messages(chat_session_id):
    try:
        return requests.get(
            f"{BASE_URL}/get-messages?chat_session_id={chat_session_id}"
        ).json().get("data", [])
    except:
        return []

def send_message(session_id, user_message):
    payload = {
        "user_id": USER_ID,
        "session_id": session_id,
        "user_message": user_message
    }
    try:
        r = requests.post(f"{BASE_URL}/ai-agent", json=payload)
        return r.json()["data"]["ai_response"]
    except:
        return "<div class='block-danger'>⚠️ Unable to reach AI service.</div>"

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("💬 Holiya Medical AI")

if st.sidebar.button("➕ Start New Session"):
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()

for s in get_sessions():
    if st.sidebar.button(f"Session {s['chat_session_id']}"):
        st.session_state.current_session_id = s["session_id"]
        st.session_state.messages = get_messages(s["chat_session_id"])
        st.rerun()

# -----------------------------
# MAIN CHAT
# -----------------------------
st.title("🩺 Holiya Medical AI Agent")

if not st.session_state.current_session_id:
    st.info("Please start or select a chat session.")
    st.stop()

st.caption(f"Session ID: `{st.session_state.current_session_id}`")
st.divider()

for msg in st.session_state.messages:
    st.markdown(
        f"<div class='user-message'><strong>You:</strong> {msg['user_message']}</div>",
        unsafe_allow_html=True
    )

    ai_html = render_message(msg['ai_response'])
    st.markdown(
        f"<div class='ai-message'><strong>Holiya AI:</strong><br>{ai_html}</div>",
        unsafe_allow_html=True
    )

st.divider()

# -----------------------------
# INPUT
# -----------------------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Write your message")
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip():
    with st.spinner("Holiya is thinking..."):
        ai_response = send_message(
            st.session_state.current_session_id,
            user_input
        )
        st.session_state.messages.append({
            "user_message": user_input,
            "ai_response": ai_response
        })
        st.rerun()
