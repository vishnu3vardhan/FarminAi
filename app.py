import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()
API_TOKEN = os.getenv("MY_SECRET_TOKEN")

API_ENDPOINT = "https://api.huggingface.co/assistants/6853beafc63a7d91a6587077/completions"


# Streamlit UI
st.set_page_config(page_title="FarminAi")
st.title("🌾 FarminAi - Your Farming Assistant")

st.write("""
Ask anything related to agriculture:
- 🌾 Crop rotation  
- 🌱 Soil health  
- 💧 Irrigation  
- 🐄 Livestock care  
- 🛒 Market tips  
""")

user_input = st.text_input("👨‍🌾 Ask your question:")

# Send request to HuggingChat Assistant API
def get_chat_response(prompt):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "top_p": 1,
        "stop": None
    }

    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error: {e}"

# Show assistant response
if st.button("🌾 Send"):
    if user_input.strip():
        with st.spinner("Thinking..."):
            reply = get_chat_response(user_input)
        st.success("💬 FarminAi says:")
        st.write(reply)
    else:
        st.warning("Please enter a question.")
