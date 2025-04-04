import time
import requests
import streamlit as st
import pandas as pd
from itertools import cycle
from functools import lru_cache

# Load Hugging Face API keys
hf_api_keys = [
    st.secrets["huggingface"]["HF_API_KEY_1"],
    st.secrets["huggingface"]["HF_API_KEY_2"],
    st.secrets["huggingface"]["HF_API_KEY_3"],
    st.secrets["huggingface"]["HF_API_KEY_4"],
]
api_key_cycle = cycle(hf_api_keys)

@lru_cache(maxsize=50)
def get_hf_response(question, model_id="mistralai/Mistral-7B-Instruct-v0.1"):
    """Fetches AI-generated responses from Hugging Face API with key cycling."""
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    
    for _ in range(len(hf_api_keys)):
        api_key = next(api_key_cycle)
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            response = requests.post(api_url, headers=headers, json={"inputs": question})
            
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 10))
                time.sleep(wait_time)
                continue  

            response.raise_for_status()
            response_data = response.json()

            if isinstance(response_data, list) and 'generated_text' in response_data[0]:
                return response_data[0]['generated_text'].strip()

        except requests.exceptions.RequestException:
            return "API Error. Please try again."

    return "Error: All API keys exhausted or failed to respond."

# Streamlit UI
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Career Roadmap Generator", "Pre-Generated Roadmaps", "Best Earning Jobs", "Career Guidance Videos", "Contact"])

# Pre-generated roadmaps with URLs and YouTube Thumbnails
pre_generated = {
    "Data Scientist": {
        "roadmap": "1. Learn Python & SQL\n2. Master statistics & ML\n3. Work on projects & Kaggle\n4. Build a strong portfolio\n5. Apply for jobs",
        "url": "https://www.datacamp.com/courses/data-science-career-track",
        "video": "https://img.youtube.com/vi/ua-CiDNNj30/0.jpg",
        "video_url": "https://www.youtube.com/watch?v=ua-CiDNNj30"
    },
    "Software Engineer": {
        "roadmap": "1. Learn programming (Python, Java, C++)\n2. Master data structures & algorithms\n3. Build projects & contribute to open source\n4. Learn system design\n5. Apply for software engineering roles",
        "url": "https://roadmap.sh/software-engineer",
        "video": "https://img.youtube.com/vi/mJ3bGvy0WAY/0.jpg",
        "video_url": "https://www.youtube.com/watch?v=mJ3bGvy0WAY"
    }
}

if page == "Career Roadmap Generator":
    job_title = st.text_input("Enter the job title:", placeholder="e.g., Data Scientist")
    submit = st.button("Generate Roadmap")
    
    if submit and job_title:
        response = get_hf_response(f"Provide a professional, step-by-step career roadmap for {job_title}.")
        with st.expander("See Full Details"):
            st.markdown(response.replace("\n", "\n\n"))

elif page == "Pre-Generated Roadmaps":
    st.header("Pre-Generated Career Roadmaps")
    for job, details in pre_generated.items():
        with st.expander(job):
            st.markdown(details["roadmap"].replace("\n", "\n\n"))
            st.markdown(f"[Reference]({details['url']})")
            st.markdown(f"[![Watch Video]({details['video']})]({details['video_url']})")

elif page == "Best Earning Jobs":
    st.header("Best Earning Jobs & Salaries")
    jobs_data = pd.DataFrame([
        {"Job Title": "Machine Learning Engineer", "Avg Salary": "$130,000"},
        {"Job Title": "Blockchain Developer", "Avg Salary": "$140,000"}
    ])
    st.dataframe(jobs_data)

elif page == "Career Guidance Videos":
    st.header("Career Guidance Videos")
    st.video("https://www.youtube.com/watch?v=ZxCvN9uOm48")
    st.video("https://www.youtube.com/watch?v=d6m-F6VYXz4")

elif page == "Contact":
    st.header("Contact Us")
    st.write("Email: support@nextleap.com")

