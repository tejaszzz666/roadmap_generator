from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import requests
from itertools import cycle

# Load Hugging Face API keys
hf_api_keys = [
    os.getenv("HF_API_KEY_1"),
    os.getenv("HF_API_KEY_2"),
    os.getenv("HF_API_KEY_3")
]
api_key_cycle = cycle(hf_api_keys)

# Function to get response from Hugging Face model
def get_hf_response(question, model_id="HuggingFaceH4/zephyr-7b-beta"):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    
    for _ in range(len(hf_api_keys)):
        api_key = next(api_key_cycle)
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            response = requests.post(api_url, headers=headers, json={"inputs": question})
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
st.set_page_config(page_title="Q&A Demo")
st.header("Reconnect")
job_title = st.text_input("Enter the job title:", key="job_title")
submit = st.button("Generate Roadmap")

input_prompt = """
You are a career guide. Please provide a step-by-step career roadmap and learning resources available on the internet for the job title: {job_title}. Present the information in bullet points.
"""

if submit:
    full_prompt = input_prompt.format(job_title=job_title)
    response = get_hf_response(full_prompt)
    st.subheader("The Response is")
    st.write(response)
