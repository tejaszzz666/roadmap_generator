import time
import requests
import streamlit as st
from itertools import cycle
from functools import lru_cache

# Load Hugging Face API keys from Streamlit secrets
hf_api_keys = [
    st.secrets["huggingface"]["HF_API_KEY_1"],
    st.secrets["huggingface"]["HF_API_KEY_2"],
    st.secrets["huggingface"]["HF_API_KEY_3"]
]
api_key_cycle = cycle(hf_api_keys)

# Function to get response from Hugging Face model with rate limiting
def get_hf_response(question, model_id="HuggingFaceH4/zephyr-7b-beta"):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"

    for _ in range(len(hf_api_keys)):
        api_key = next(api_key_cycle)
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            response = requests.post(api_url, headers=headers, json={"inputs": question})

            # If rate limited, wait and retry
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 10))  # Default wait: 10 sec
                st.warning(f"Rate limit hit! Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue  # Try next key

            response.raise_for_status()
            response_data = response.json()

            if isinstance(response_data, list) and 'generated_text' in response_data[0]:
                return response_data[0]['generated_text']
            else:
                return f"Unexpected response format: {response_data}"

        except requests.exceptions.RequestException as e:
            return f"API Error: {e}"

    return "Error: All API keys exhausted or failed to respond."

# ✅ CACHE API RESULTS FOR 1 HOUR
@st.cache_data(ttl=3600)  # Cache results for 1 hour
def get_cached_hf_response(question):
    return get_hf_response(question)

# Streamlit UI
st.set_page_config(page_title="Reconnect - Career Guide", page_icon="🚀", layout="wide")

st.title("🚀 Reconnect: Career Roadmap Generator")
st.markdown("Get a **step-by-step career roadmap** with learning resources based on your job title!")

job_title = st.text_input("🔍 Enter the job title:", key="job_title")
submit = st.button("Generate Roadmap 🚀")

if submit:
    full_prompt = f"You are a career guide. Provide a roadmap for: {job_title}."
    
    # Use cached API response
    response = get_cached_hf_response(full_prompt)

    st.subheader("📌 Your Career Roadmap")
    with st.expander("See the Full Details 📜"):
        st.write(response)

    st.success("✅ Roadmap Generated! Keep Learning & Growing 🎯")
