import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load .env for secret token
load_dotenv()
API_TOKEN = os.getenv("MY_SECRET_TOKEN")

# Fixed model: Zephyr
MODEL_NAME = "HuggingFaceH4/zephyr-7b-beta"

# Initialize session state
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []

# Page config
st.set_page_config(
    page_title="FarminAi - Farming Assistant",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobile-friendly CSS
st.markdown("""
<style>
.chat-message {
    padding: 1rem;
    border-radius: 0.75rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    font-size: 1.05rem;
    word-wrap: break-word;
}
.user-message {
    background-color: #e8f5e9;
    border-left: 4px solid #43a047;
}
.assistant-message {
    background-color: #f1f8e9;
    border-left: 4px solid #558b2f;
}
.message-header {
    font-weight: 600;
    color: #33691e;
    margin-bottom: 0.3rem;
}
.message-content {
    color: #2e7d32;
    line-height: 1.6;
}
@media (max-width: 768px) {
    .chat-message {
        font-size: 1rem;
        padding: 0.75rem;
    }
}
</style>
""", unsafe_allow_html=True)

# Format messages
def format_message(role: str, content: str):
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-header">👨‍🌾 Farmer</div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <div class="message-header">🤖 FarminAi</div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)

# Query the Hugging Face API
def query_model(prompt: str, model: str) -> str:
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

    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result[0].get("generated_text", "Sorry, I couldn’t understand your question.").strip()
    except requests.exceptions.RequestException as e:
        return f"❌ Network Error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"

# MAIN APP
init_session()
st.title("🌱 FarminAi")
st.markdown("Your friendly farming assistant for Indian agriculture.")



# Display previous chat
for msg in st.session_state.messages:
    format_message(msg["role"], msg["content"])

# Chat input
user_input = st.chat_input("👨‍🌾 Ask about crops, pests, weather, or soil...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    format_message("user", user_input)

    with st.spinner("🤖 FarminAi is thinking..."):
        response = query_model(user_input, MODEL_NAME)

    st.session_state.messages.append({"role": "assistant", "content": response})
    format_message("assistant", response)
    st.rerun()

# --- Mobile Fixes ---

# Add bottom padding on mobile to prevent keyboard overlap
st.markdown("""
<style>
@media (max-width: 768px) {
    .block-container {
        padding-bottom: 120px;  /* Extra space for keyboard */
    }
}
</style>
""", unsafe_allow_html=True)

# Scroll chat input into view when focused
st.markdown("""
<script>
const chatInput = window.parent.document.querySelector('input[type="text"]');
if (chatInput) {
  chatInput.addEventListener('focus', () => {
    setTimeout(() => {
      window.scrollTo(0, document.body.scrollHeight);
    }, 300);
  });
}
</script>
""", unsafe_allow_html=True)