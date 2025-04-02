import time
import requests
import streamlit as st
from itertools import cycle

# Load Hugging Face API keys from Streamlit secrets
hf_api_keys = [
    st.secrets["huggingface"]["HF_API_KEY_1"],
    st.secrets["huggingface"]["HF_API_KEY_2"],
    st.secrets["huggingface"]["HF_API_KEY_3"]
]
api_key_cycle = cycle(hf_api_keys)

def get_hf_response(question, model_id="HuggingFaceH4/zephyr-7b-beta"):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    
    for _ in range(len(hf_api_keys)):
        api_key = next(api_key_cycle)
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            response = requests.post(api_url, headers=headers, json={"inputs": question})

            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 10))
                st.warning(f"Rate limit hit. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            response_data = response.json()

            if isinstance(response_data, list) and 'generated_text' in response_data[0]:
                return response_data[0]['generated_text']
            else:
                return f"Unexpected response format: {response_data}"

        except requests.exceptions.RequestException as e:
            return f"API Error: {e}"

    return "Error: All API keys exhausted or failed to respond."

# Streamlit Multi-Page App Setup
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Roadmap", "Resources", "About"])

# Custom CSS for Sleek Design
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: white;
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #1f1c2c 0%, #928dab 100%);
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
    .title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

if page == "Home":
    st.markdown('<h1 class="title">NextLeap: Career Roadmap Generator</h1>', unsafe_allow_html=True)
    st.write("Get a structured career roadmap with learning resources tailored to your job title.")
    
    job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")
    submit = st.button("Generate Roadmap")

    if submit:
        st.session_state["roadmap"] = get_hf_response(f"You are a career guide. Provide a roadmap for: {job_title}.")
        st.success("Roadmap generated successfully. Go to the 'Roadmap' page to view it.")

elif page == "Roadmap":
    st.markdown('<h1 class="title">Generated Roadmap</h1>', unsafe_allow_html=True)
    if "roadmap" in st.session_state:
        st.subheader("Career Roadmap")
        with st.expander("See Full Details"):
            st.write(st.session_state["roadmap"])
    else:
        st.warning("No roadmap generated yet. Please go to 'Home' and enter a job title.")

elif page == "Resources":
    st.markdown('<h1 class="title">Resources</h1>', unsafe_allow_html=True)
    st.write("Explore learning resources for different career paths:")
    st.markdown("- **Data Science**: [Coursera](https://www.coursera.org/), [Kaggle](https://www.kaggle.com/)")
    st.markdown("- **Software Engineering**: [LeetCode](https://leetcode.com/), [CS50](https://cs50.harvard.edu/)")
    st.markdown("- **Cybersecurity**: [TryHackMe](https://tryhackme.com/), [Cybrary](https://www.cybrary.it/)")

elif page == "About":
    st.markdown('<h1 class="title">About</h1>', unsafe_allow_html=True)
    st.write("NextLeap is an AI-powered career roadmap generator. It provides structured guidance on career paths, required skills, and learning resources to help users achieve their professional goals.")
