# 🌱 FarminAi - Your Farming Assistant

**FarminAi** is a smart, conversational AI assistant built with **Streamlit** and **Hugging Face models**, aimed at helping Indian farmers with practical advice on crops, soil, weather, pests, irrigation, schemes, and more.

---

## 🚀 Features

- 🤖 Conversational assistant for agriculture
- 🌾 Choose from models like:
  - `microsoft/DialoGPT-medium`
  - `microsoft/DialoGPT-large`
  - `mistralai/Mistral-7B-Instruct-v0.1`
- 🧠 Adjustable settings:
  - Max tokens
  - Temperature
  - Top-p
- ✅ Check model availability
- 💬 Styled, persistent chat history
- 🗑️ Clear chat functionality

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/farminai.git
cd farminai
```
### 2. Create & Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
### 3. Install Dependencies and Add Hugging face Token
```bash
pip install -r requirements.txt
```
### 4. create a .env file and HF token
```bash
MY_SECRET_TOKEN=your_huggingface_api_token
```
### 5. RUN the app
```bash
streamlit run app.py
```
 ## Sample Questions
"Which fertilizer is best for sugarcane in black soil?"

"How do I prevent pests in brinjal crops?"

"Any subsidies for organic farming in Tamil Nadu?"

## Tech Stack
Streamlit

Hugging Face Inference API

Python

dotenv



### 👤 Author
Vishnu Vardhan
GitHub: vishnu3vardhan


