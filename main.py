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
    password_input = st.text_input(
        "Enter password",
        type="password"
    )
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
# STYLES 
# ----------------------------- 
st.markdown("""
<style>
    .user-message {
        background-color: #e3f2fd;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        border-left: 4px solid #2196f3;
    }
    .ai-message {
        background-color: #f5f5f5;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        border-left: 4px solid #4caf50;
    }
    .ai-message ul, .ai-message ol {
        margin: 10px 0;
        padding-left: 20px;
    }
    .ai-message li {
        margin: 5px 0;
    }
    .ai-message p {
        margin: 8px 0;
    }
    .ai-message strong {
        font-weight: 600;
        color: #1a1a1a;
    }
    .ai-message em {
        font-style: italic;
    }
    .ai-message h1, .ai-message h2, .ai-message h3 {
        margin-top: 16px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------- 
# HELPER FUNCTIONS
# ----------------------------- 
def is_html(text):
    """Check if text contains HTML tags"""
    html_pattern = re.compile(r'<[^>]+>')
    return bool(html_pattern.search(text))

def markdown_to_html(text):
    """Convert basic markdown to HTML"""
    if not text:
        return ""
    
    # Bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    
    # Italic: *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    
    # Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Line breaks
    text = text.replace('\n', '<br>')
    
    return text

def render_message(text):
    """Render message as HTML (handles both HTML and markdown)"""
    if not text:
        return ""
    
    # If already HTML, return as-is
    if is_html(text):
        return text
    
    # Otherwise, convert markdown to HTML
    return markdown_to_html(text)

# ----------------------------- 
# API FUNCTIONS 
# ----------------------------- 
def get_sessions():
    try:
        url = f"{BASE_URL}/get-sessions?user_id={USER_ID}"
        return requests.get(url).json().get("data", [])
    except Exception:
        return []

def get_messages(chat_session_id):
    try:
        url = f"{BASE_URL}/get-messages?chat_session_id={chat_session_id}"
        return requests.get(url).json().get("data", [])
    except Exception:
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
    except Exception:
        return "⚠️ Unable to reach AI service."

# ----------------------------- 
# SESSION STATE INIT 
# ----------------------------- 
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "current_chat_db_id" not in st.session_state:
    st.session_state.current_chat_db_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------- 
# SIDEBAR 
# ----------------------------- 
st.sidebar.title("💬 Holiya Medical AI")
st.sidebar.subheader("Chat Sessions")

# Start New Session
if st.sidebar.button("➕ Start New Session"):
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.current_chat_db_id = None
    st.session_state.messages = []
    st.rerun()

# Existing Sessions
sessions = get_sessions()
for s in sessions:
    db_id = s["chat_session_id"]
    session_uuid = s["session_id"]
    label = f"Session {db_id} — {session_uuid[:8]}"
    if st.sidebar.button(label, key=db_id):
        st.session_state.current_session_id = session_uuid
        st.session_state.current_chat_db_id = db_id
        st.session_state.messages = get_messages(db_id)
        st.rerun()

# ----------------------------- 
# MAIN CHAT 
# ----------------------------- 
st.title("🩺 Holiya Medical AI Agent")

if not st.session_state.current_session_id:
    st.info("Create or select a chat session from the sidebar.")
    st.stop()

st.caption(f"Session ID: `{st.session_state.current_session_id}`")
st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)

# Display Messages
for msg in st.session_state.messages:
    # User message
    user_msg = msg.get('user_message', '')
    st.markdown(
        f"<div class='user-message'><strong>You:</strong> {user_msg}</div>",
        unsafe_allow_html=True
    )
    
    # AI response with proper rendering
    ai_msg = msg.get('ai_response', '')
    rendered_ai_msg = render_message(ai_msg)
    st.markdown(
        f"<div class='ai-message'><strong>Holiya AI:</strong><br>{rendered_ai_msg}</div>",
        unsafe_allow_html=True
    )

st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
st.divider()

# ----------------------------- 
# MESSAGE INPUT 
# ----------------------------- 
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Write your message")
    send_btn = st.form_submit_button("Send")

if send_btn and user_input.strip():
    with st.spinner("Holiya Agent is thinking..."):
        ai_response = send_message(
            st.session_state.current_session_id,
            user_input
        )
        
        st.session_state.messages.append({
            "user_message": user_input,
            "ai_response": ai_response
        })
        st.rerun()
