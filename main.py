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
    /* Light background for main chat area */
    .main {
        background-color: #f8f9fa;
    }
    
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* User message bubble */
    .user-message {
        background-color: #e3f2fd;
        padding: 14px 18px;
        border-radius: 16px;
        margin: 12px 0;
        border-left: 5px solid #2196f3;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        color: #1565c0;
    }
    
    /* AI message bubble */
    .ai-message {
        background-color: #ffffff;
        padding: 14px 18px;
        border-radius: 16px;
        margin: 12px 0;
        border-left: 5px solid #4caf50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    
    /* Colored content blocks with colored text */
    .block-info {
        background-color: #e3f2fd;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 4px solid #2196f3;
        color: #0d47a1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .block-success {
        background-color: #e8f5e9;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 4px solid #4caf50;
        color: #1b5e20;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .block-warning {
        background-color: #fff3e0;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 4px solid #ff9800;
        color: #e65100;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .block-danger {
        background-color: #ffebee;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 4px solid #f44336;
        color: #b71c1c;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .block-primary {
        background-color: #f3e5f5;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 4px solid #9c27b0;
        color: #4a148c;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .block-secondary {
        background-color: #f5f5f5;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 4px solid #757575;
        color: #424242;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .block-teal {
        background-color: #e0f2f1;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 4px solid #009688;
        color: #004d40;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .block-indigo {
        background-color: #e8eaf6;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 4px solid #3f51b5;
        color: #1a237e;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    
    /* Text colors for inline use */
    .text-blue { color: #0d47a1; font-weight: 600; }
    .text-green { color: #1b5e20; font-weight: 600; }
    .text-orange { color: #e65100; font-weight: 600; }
    .text-red { color: #b71c1c; font-weight: 600; }
    .text-purple { color: #4a148c; font-weight: 600; }
    .text-teal { color: #004d40; font-weight: 600; }
    .text-indigo { color: #1a237e; font-weight: 600; }
    .text-grey { color: #424242; font-weight: 500; }
    
    /* Typography */
    .ai-message ul, .ai-message ol,
    .block-info ul, .block-info ol,
    .block-success ul, .block-success ol,
    .block-warning ul, .block-warning ol,
    .block-danger ul, .block-danger ol,
    .block-primary ul, .block-primary ol,
    .block-secondary ul, .block-secondary ol,
    .block-teal ul, .block-teal ol,
    .block-indigo ul, .block-indigo ol {
        margin: 10px 0;
        padding-left: 20px;
    }
    
    .ai-message li,
    .block-info li, .block-success li, .block-warning li,
    .block-danger li, .block-primary li, .block-secondary li,
    .block-teal li, .block-indigo li {
        margin: 6px 0;
        line-height: 1.6;
    }
    
    .ai-message p,
    .block-info p, .block-success p, .block-warning p,
    .block-danger p, .block-primary p, .block-secondary p,
    .block-teal p, .block-indigo p {
        margin: 8px 0;
        line-height: 1.7;
    }
    
    .ai-message strong,
    .block-info strong, .block-success strong, .block-warning strong,
    .block-danger strong, .block-primary strong, .block-secondary strong,
    .block-teal strong, .block-indigo strong {
        font-weight: 700;
    }
    
    .ai-message em,
    .block-info em, .block-success em, .block-warning em,
    .block-danger em, .block-primary em, .block-secondary em,
    .block-teal em, .block-indigo em {
        font-style: italic;
    }
    
    .ai-message h1, .ai-message h2, .ai-message h3,
    .block-info h1, .block-info h2, .block-info h3,
    .block-success h1, .block-success h2, .block-success h3,
    .block-warning h1, .block-warning h2, .block-warning h3,
    .block-danger h1, .block-danger h2, .block-danger h3,
    .block-primary h1, .block-primary h2, .block-primary h3,
    .block-secondary h1, .block-secondary h2, .block-secondary h3,
    .block-teal h1, .block-teal h2, .block-teal h3,
    .block-indigo h1, .block-indigo h2, .block-indigo h3 {
        margin-top: 14px;
        margin-bottom: 10px;
        font-weight: 700;
    }
    
    /* Inline highlights */
    .highlight {
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .highlight-blue { background-color: #bbdefb; color: #0d47a1; }
    .highlight-green { background-color: #c8e6c9; color: #1b5e20; }
    .highlight-orange { background-color: #ffe0b2; color: #e65100; }
    .highlight-red { background-color: #ffcdd2; color: #b71c1c; }
    .highlight-purple { background-color: #e1bee7; color: #4a148c; }
    .highlight-teal { background-color: #b2dfdb; color: #004d40; }
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
