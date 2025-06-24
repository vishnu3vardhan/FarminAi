import streamlit as st
import requests
import os
import json
import time
from dotenv import load_dotenv
from typing import Dict

# Load .env for secret token
load_dotenv()
API_TOKEN = os.getenv("MY_SECRET_TOKEN")

# Available Models (focused for conversational AI in agriculture)
AVAILABLE_MODELS = {
    "DialoGPT Medium": "microsoft/DialoGPT-medium",
    "DialoGPT Large": "microsoft/DialoGPT-large",
    "Mistral Instruct": "mistralai/Mistral-7B-Instruct-v0.1"
}

# Initialize session state
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model_path" not in st.session_state:
        st.session_state.model_path = AVAILABLE_MODELS["DialoGPT Medium"]

# Custom styling
st.set_page_config(page_title="FarminAi - Farming Assistant", layout="wide")
st.markdown("""
<style>
.chat-message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
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
    font-weight: bold;
    color: #33691e;
    margin-bottom: 0.3rem;
}
.message-content {
    color: #2e7d32;
    line-height: 1.6;
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

# Test model availability
def test_model_availability(model: str) -> bool:
    endpoint = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    try:
        payload = {"inputs": "ping"}
        response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False

# Query the Hugging Face API
def query_model(prompt: str, model: str, temperature=0.7, top_p=0.9, max_length=200) -> str:
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
            "max_new_tokens": max_length,
            "temperature": temperature,
            "top_p": top_p,
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
st.title("🌱 FarminAi - Your Farming Assistant")
st.markdown("Helping Indian farmers with intelligent, accurate, and localized agriculture advice.")

# Sidebar settings
with st.sidebar:
    st.header("🌾 FarminAi Settings")

    selected_model = st.selectbox("Select AI Model:", list(AVAILABLE_MODELS.keys()))
    st.session_state.model_path = AVAILABLE_MODELS[selected_model]

    if st.button("Test Model Availability"):
        with st.spinner("Checking availability..."):
            if test_model_availability(st.session_state.model_path):
                st.success("✅ Model is available!")
            else:
                st.error("❌ Model not responding or unavailable.")

    st.markdown("---")
    max_length = st.slider("Max Tokens", 50, 500, 200)
    temperature = st.slider("Temperature", 0.1, 1.5, 0.7)
    top_p = st.slider("Top-p (nucleus sampling)", 0.1, 1.0, 0.9)

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages.clear()

# Display previous chat
for msg in st.session_state.messages:
    format_message(msg["role"], msg["content"])

# Chat input
user_input = st.chat_input("👨‍🌾 Ask about crops, pests, weather, or soil...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    format_message("user", user_input)

    with st.spinner("🤖 FarminAi is thinking..."):
        response = query_model(user_input, st.session_state.model_path, temperature, top_p, max_length)

    st.session_state.messages.append({"role": "assistant", "content": response})
    format_message("assistant", response)
    st.rerun()  # Improved session state update
