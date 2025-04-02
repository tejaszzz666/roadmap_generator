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
]
api_key_cycle = cycle(hf_api_keys)

# Caching API responses to prevent key exhaustion
@lru_cache(maxsize=10)
def get_hf_response(question, model_id="mistralai/Mistral-7B-Instruct"):
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

# Streamlit setup
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")

# UI Design
st.markdown("<h1 style='text-align: center; color: white;'>NextLeap: Career Roadmap Generator</h1>", unsafe_allow_html=True)
st.write("Get a structured career roadmap with learning resources tailored to your job title.")

# Input field
job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")

# Generate button
submit = st.button("Generate Roadmap")

# Input prompt template
input_prompt = """
You are a career guide. Please provide a professional, step-by-step career roadmap and learning resources available on the internet for the job title: {job_title}. Present the information in bullet points.
"""

if submit:
    full_prompt = input_prompt.format(job_title=job_title)
    response = get_hf_response(full_prompt)

    # Display response
    st.subheader("Career Roadmap")
    with st.expander("See Full Details"):
        st.markdown(response.replace("\n", "\n\n"))

    st.success("Roadmap generated successfully.")
