import streamlit as st
import requests
import os
import time
from dotenv import load_dotenv

# Load .env for secret token
load_dotenv()
API_TOKEN = os.getenv("MY_SECRET_TOKEN")

# Model name
MODEL_NAME = "HuggingFaceH4/zephyr-7b-beta"

# Initialize session state
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []

# Optional: Pre-warm the model to reduce first-response lag
@st.cache_resource
def prewarm_model():
    try:
        _ = query_model("Hello", MODEL_NAME, retries=1, timeout=20)
    except Exception:
        pass

# Page configuration
st.set_page_config(
    page_title="FarminAi - Farming Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
    background-color: #f5f9f6;
    color: #2e3c3a;
}
.chat-bubble {
    padding: 1rem;
    border-radius: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.user-bubble {
    background: #d1ecf1;
    border-left: 6px solid #17a2b8;
    color: #0c5460;
}
.assistant-bubble {
    background: #e8f5e9;
    border-left: 6px solid #4caf50;
    color: #2e7d32;
}
.chat-bubble:hover {
    transform: scale(1.02);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}
.header {
    font-weight: bold;
    margin-bottom: 0.25rem;
    font-size: 1.1rem;
}
.body-text {
    line-height: 1.65;
    font-size: 1.02rem;
}
.new-chat-button {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1rem;
}
button[kind="primary"] {
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    transition: background-color 0.3s ease;
}
button[kind="primary"]:hover {
    background-color: #388e3c;
}
</style>
""", unsafe_allow_html=True)

# Format chat messages
def format_message(role: str, content: str):
    bubble_class = "user-bubble" if role == "user" else "assistant-bubble"
    name = "You" if role == "user" else "FarminAi"
    st.markdown(f"""
    <div class="chat-bubble {bubble_class}">
        <div class="header">{name}</div>
        <div class="body-text">{content}</div>
    </div>
    """, unsafe_allow_html=True)

# Query Hugging Face model with retry + cleanup
def query_model(prompt: str, model: str, retries=3, timeout=60) -> str:
    endpoint = f"https://api-inference.huggingface.co/models/{model}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are FarminAi, an AI assistant for farmers. Provide clear, practical, and localized advice "
        "on farming, soil, weather, crops, irrigation, pest control, government schemes, and market prices. "
        "Respond with kindness, simplicity, and accuracy in English."
    )

    message = f"{system_prompt}\nFarmer: {prompt}\nFarminAi:"

    payload = {
        "inputs": message,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "return_full_text": False,
            "stop": ["Farmer:", "FarminAi:"]
        }
    }

    for attempt in range(retries):
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            result = response.json()
            raw_output = result[0].get("generated_text", "").strip()
            cleaned_output = raw_output.split("Farmer:")[0].split("FarminAi:")[0].strip()
            return cleaned_output if cleaned_output else "Sorry, I couldn't understand your question."
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return "❌ Error: Hugging Face model timed out. Please try again shortly."
        except requests.exceptions.RequestException as e:
            return f"❌ Network Error: {e}"
        except Exception as e:
            return f"❌ Unexpected Error: {e}"

# Initialize session + prewarm
init_session()
prewarm_model()

# --- Header ---
st.title("🌾 FarminAi - Your Smart Farming Assistant")
st.markdown("Ask me anything about farming — crops, weather, soil, pests, and more!")

# --- New Chat Button ---
with st.container():
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("🔁 New Chat"):
            st.session_state.messages = []
            st.rerun()

# --- Chat history ---
for msg in st.session_state.messages:
    format_message(msg["role"], msg["content"])

# --- Chat input ---
user_input = st.chat_input("👨‍🌾 Ask me anything about farming.")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    format_message("user", user_input)

    with st.spinner("FarminAi is thinking..."):
        response = query_model(user_input, MODEL_NAME)

    st.session_state.messages.append({"role": "assistant", "content": response})
    format_message("assistant", response)
    st.rerun()

# --- Mobile UI Optimization ---
st.markdown("""
<style>
@media (max-width: 768px) {
    .block-container {
        padding-bottom: 120px !important;
        padding-left: 16px !important;
        padding-right: 16px !important;
    }
    .css-18e3th9 {
        font-size: 16px !important;
    }
    button {
        font-size: 16px;
        padding: 10px 20px;
    }
    input[type="text"] {
        font-size: 18px;
        padding: 12px;
        width: 100%;
        margin-bottom: 10px;
    }
}
html {
    scroll-behavior: smooth;
}
</style>
""", unsafe_allow_html=True)

# --- Auto Scroll on Input ---
st.markdown("""
<script>
const chatInput = window.parent.document.querySelector('input[type="text"]');
if (chatInput) {
  chatInput.addEventListener('focus', () => {
    setTimeout(() => {
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }, 300);
  });
}
</script>
""", unsafe_allow_html=True)
