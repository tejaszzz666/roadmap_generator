import streamlit as st
import requests
import time
from itertools import cycle
from functools import lru_cache

# 🔹 Hugging Face API Keys (Cycle to Bypass Rate Limits)
hf_api_keys = [
    st.secrets["huggingface"]["HF_API_KEY_1"],
    st.secrets["huggingface"]["HF_API_KEY_2"],
    st.secrets["huggingface"]["HF_API_KEY_3"],
    st.secrets["huggingface"]["HF_API_KEY_4"]
]
api_key_cycle = cycle(hf_api_keys)

# 🔹 Caching AI Responses (Optimized Hugging Face API Call)
@lru_cache(maxsize=50)
def get_hf_response(question, model_id="mistralai/Mistral-7B-Instruct-v0.1"):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    for _ in range(len(hf_api_keys)):
        api_key = next(api_key_cycle)
        headers = {"Authorization": f"Bearer {api_key}"}

        retry_attempts = 3
        for attempt in range(retry_attempts):
            response = requests.post(api_url, headers=headers, json={"inputs": question})
            if response.status_code == 200:
                return response.json()[0].get("generated_text", "No response generated")
            elif response.status_code == 429:  # Rate Limit Handling
                wait_time = 2 ** attempt  # Exponential Backoff (2s, 4s, 8s)
                time.sleep(wait_time)
            else:
                break
    return "Error: All API keys failed."

# 🔹 Fetch Jobs from API (Fix: Corrected API URL)
def fetch_jobs(query):
    api_url = f"https://jsearch.p.rapidapi.com/search?query={query}&location=India"
    headers = {"X-RapidAPI-Key": "your-rapidapi-key"}
    response = requests.get(api_url, headers=headers)
    return response.json() if response.status_code == 200 else {"error": "Failed to fetch jobs"}

# 🔹 Community Forum (Basic Post System Without Database)
st.title("Community Forum")

# Simple Forum Posts List (Temporary, Not Stored)
if "forum_posts" not in st.session_state:
    st.session_state.forum_posts = []

new_question = st.text_area("Ask a question:")
if st.button("Post"):
    if new_question:
        st.session_state.forum_posts.append({"question": new_question, "upvotes": 0})
        st.success("Question posted successfully!")

# Display Forum Posts
st.subheader("Recent Questions:")
for i, post in enumerate(st.session_state.forum_posts):
    st.write(f"**{post['question']}**")
    if st.button(f"Upvote ({post['upvotes']})", key=i):
        st.session_state.forum_posts[i]["upvotes"] += 1

# 🔹 Dark Mode & Animations (Fix: Improved Styling)
dark_mode = st.toggle("Dark Mode")

if dark_mode:
    st.markdown("""
    <style>
        body { background-color: #121212; color: white; }
        .stButton>button { transition: 0.3s; background-color: #333; color: white; }
        .stButton>button:hover { transform: scale(1.05); background-color: #555; }
    </style>
    """, unsafe_allow_html=True)
