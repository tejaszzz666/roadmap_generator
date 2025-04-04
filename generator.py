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
                st.warning(f"Rate limit hit. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue  

            response.raise_for_status()
            response_data = response.json()

            if isinstance(response_data, list) and 'generated_text' in response_data[0]:
                output = response_data[0]['generated_text']
                if output.startswith(question):
                    output = output[len(question):].strip()
                return output

        except requests.exceptions.RequestException as e:
            return f"API Error: {e}"

    return "Error: All API keys exhausted or failed to respond."

# Streamlit UI
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
nav_selection = st.sidebar.radio("Go to:", ["Home", "Pre-Generated Roadmaps", "Best Earning Jobs", "Contact", "Videos"])

# Tabs
if nav_selection == "Pre-Generated Roadmaps":
    st.title("Pre-Generated Career Roadmaps")
    pre_generated = {
        "Data Scientist": {
            "roadmap": "1. Learn Python & SQL\n2. Study Data Analysis and Visualization\n3. Master Machine Learning (Scikit-Learn, TensorFlow, PyTorch)\n4. Work on Projects and Kaggle Competitions\n5. Gain Experience & Apply for Jobs",
            "url": "https://www.coursera.org/specializations/data-science",
            "video": "https://www.youtube.com/watch?v=ua-CiDNNj30"
        },
        "Software Engineer": {
            "roadmap": "1. Learn Programming (Python, Java, C++)\n2. Understand Data Structures and Algorithms\n3. Build Projects and Contribute to Open Source\n4. Master System Design & Databases\n5. Apply for Internships and Jobs",
            "url": "https://roadmap.sh/software-engineer",
            "video": "https://www.youtube.com/watch?v=mrHNSanmqQ4"
        },
    }
    
    for job, details in pre_generated.items():
        st.subheader(job)
        st.markdown(details["roadmap"].replace("\n", "\n\n"))
        st.markdown(f"[Reference: {job} Roadmap]({details['url']})")
        st.video(details["video"])
        st.markdown("---")

elif nav_selection == "Best Earning Jobs":
    st.title("Best Earning Jobs & Salaries")
    jobs_data = [
        {"Job Title": "Machine Learning Engineer", "Avg Salary": "$130,000"},
        {"Job Title": "Blockchain Developer", "Avg Salary": "$140,000"},
    ]
    df = pd.DataFrame(jobs_data)
    st.dataframe(df)

elif nav_selection == "Contact":
    st.title("Contact Us")
    st.write("Email: support@nextleap.com")
    st.write("Phone: +1 234 567 890")
    st.write("Website: [NextLeap](https://nextleap.com)")

elif nav_selection == "Videos":
    st.title("Career Guidance Videos")
    if "video_links" in st.session_state:
        for link in st.session_state["video_links"]:
            st.video(link)
    else:
        st.write("Generate a roadmap to see relevant videos.")

else:
    st.title("Career Roadmap Generator")
    job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")
    submit = st.button("Generate Roadmap")
    
    if submit and job_title:
        input_prompt = f"Provide a professional, step-by-step career roadmap for {job_title}. Include reference URLs if available."
        response = get_hf_response(input_prompt)
        
        st.subheader("Career Roadmap")
        with st.expander("See Full Details"):
            st.markdown(response.replace("\n", "\n\n"))
        st.success("Roadmap generated successfully.")

        # Fetch YouTube Video Links
        video_prompt = f"List 3-4 best YouTube video links for career guidance in {job_title}."
        video_response = get_hf_response(video_prompt)
        video_links = [link.strip() for link in video_response.split("\n") if link.startswith("http")]
        
        # Store videos in session state
        st.session_state["video_links"] = video_links
