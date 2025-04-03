import time
import requests
import streamlit as st
from itertools import cycle
from functools import lru_cache

# Load Hugging Face API keys from Streamlit secrets
hf_api_keys = [
    st.secrets["huggingface"]["HF_API_KEY_1"],
    st.secrets["huggingface"]["HF_API_KEY_2"],
    st.secrets["huggingface"]["HF_API_KEY_3"],
    st.secrets["huggingface"]["HF_API_KEY_4"],
    st.secrets["huggingface"]["HF_API_KEY_5"]
]
api_key_cycle = cycle(hf_api_keys)

# Caching API responses to prevent key exhaustion
@lru_cache(maxsize=50)
def get_hf_response(question, model_id="mistralai/Mistral-7B-Instruct-v0.1"):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"

    for _ in range(len(hf_api_keys)):
        api_key = next(api_key_cycle)
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            response = requests.post(api_url, headers=headers, json={"inputs": question})
            
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

# Streamlit setup
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")

# Dark Mode Styling
st.markdown(
    """
    <style>
    body {background-color: #121212; color: white;}
    .stTextInput, .stButton {border-radius: 10px;}
    </style>
    """, unsafe_allow_html=True
)

# UI with Tabs
st.markdown("<h1 style='text-align: center;'>NextLeap: Career Roadmap Generator</h1>", unsafe_allow_html=True)
st.write("Get a structured career roadmap with learning resources tailored to your job title.")

# Tabs
tab1, tab2, tab3 = st.tabs(["Career Roadmap", "Resources", "Job Listings"])

with tab1:
    job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")
    submit = st.button("Generate Roadmap")
    
    input_prompt = f"""
    You are a career guide. Provide a professional, step-by-step career roadmap and learning resources for {job_title}. Present it in bullet points.
    """
    
    if submit:
        response = get_hf_response(input_prompt)
        st.subheader("Career Roadmap")
        with st.expander("See Full Details"):
            st.markdown(response.replace("\n", "\n\n"))
        
        st.success("Roadmap generated successfully.")

with tab2:
    st.write("Additional learning resources will be added here.")

with tab3:
    st.write("Live job listings will be fetched from APIs here.")
