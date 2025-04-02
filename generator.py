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
@st.cache_data
def get_hf_response(question, model_id="meta-llama/Llama-2-7b-chat-hft"):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"

    for _ in range(len(hf_api_keys)):
        api_key = next(api_key_cycle)
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            response = requests.post(api_url, headers=headers, json={"inputs": question})

            # If rate limited, wait and retry
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 10))  # Default wait: 10 sec
                st.warning(f"Rate limit hit. Retrying in {wait_time} seconds...")
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

# Streamlit Setup
st.set_page_config(page_title="Reconnect - Career Guide", layout="wide")

# Custom CSS for a modern design
st.markdown("""
    <style>
    body {
        background-color: #000000;
        color: white;
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: #000000;
        padding: 20px;
        border-radius: 20px;
    }
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 12px;
        color: white;
    }
    .stButton>button {
        background: linear-gradient(90deg, #ff7eb3 0%, #ff758c 100%);
        color: white;
        font-size: 18px;
        border-radius: 12px;
        padding: 12px;
        transition: 0.3s ease-in-out;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #ff758c 0%, #ff7eb3 100%);
        transform: scale(1.05);
    }
    .stExpander {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 10px;
    }
    .title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# UI Layout
st.markdown('<h1 class="title">NextLeap : Career Roadmap Generator</h1>', unsafe_allow_html=True)
st.write("Get a structured career roadmap with learning resources tailored to your job title.")

# Input Field
job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")

# Generate Button
submit = st.button("Generate Roadmap")

if submit:
    full_prompt = f"You are a career guide. Provide a detailed step-by-step roadmap for: {job_title}."  
    
    # API Call
    response = get_hf_response(full_prompt)
    
    # Response UI
    st.subheader("Career Roadmap")
    roadmap_steps = response.split("\n")
    for step in roadmap_steps:
        if step.strip():
            st.write(f"- {step}")

    st.success("Roadmap generated successfully.")
