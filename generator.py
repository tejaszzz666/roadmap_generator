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
    
    for _ in range(len(hf_api_keys)):  # Cycle through all API keys
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

# Ferrari-Themed Styling
st.markdown(
    """
    <style>
    body {background-color: #000000; color: white; font-family: 'Arial', sans-serif;}
    .stTextInput > div > div > input {
        border: 2px solid red;
        border-radius: 10px;
        background-color: #1c1c1c;
        color: white;
        padding: 10px;
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: bold;
        background: red;
        color: white;
        padding: 10px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background: yellow;
        color: black;
    }
    h1 {
        text-align: center;
        font-size: 50px;
        color: red;
        font-weight: bold;
    }
    .stTabs {
        background-color: #1c1c1c;
        border-radius: 10px;
        padding: 10px;
    }
    .nav-container {
        background: red;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    .nav-container a {
        text-decoration: none;
        color: white;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 5px;
        background: black;
        margin: 5px;
    }
    .nav-container a:hover {
        background: yellow;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True
)

# ---- Navigation Bar ----
st.markdown("""
<div class='nav-container'>
    <a href='/?nav=roadmap'>Pre-Generated Roadmaps</a>
    <a href='/?nav=bestjobs'>Best Earning Jobs</a>
    <a href='/?nav=contact'>Contact</a>
</div>
""", unsafe_allow_html=True)

# ---- Main UI ----
st.markdown("<h1>NextLeap: Career Roadmap Generator</h1>", unsafe_allow_html=True)
st.write("Get a structured career roadmap with learning resources tailored to your job title.")

nav_selection = st.experimental_get_query_params().get("nav", ["home"])[0]

if nav_selection == "roadmap":
    st.subheader("🏁 Pre-Generated Career Roadmaps")
    pre_generated = {
        "Data Scientist": "Analyze data, learn Python, master ML...",
        "Software Engineer": "Learn coding, get experience, build projects...",
        "Cybersecurity Expert": "Understand threats, learn ethical hacking...",
        "AI Engineer": "Master AI/ML, study deep learning...",
        "Product Manager": "Develop leadership, understand UX, analyze market...",
    }
    
    for job, roadmap in pre_generated.items():
        with st.expander(f"{job} Roadmap"):
            st.write(roadmap)

elif nav_selection == "bestjobs":
    st.subheader("Best Earning Jobs & Salaries")
    jobs_data = [
        {"Job Title": "Machine Learning Engineer", "Avg Salary": "$130,000"},
        {"Job Title": "Blockchain Developer", "Avg Salary": "$140,000"},
        {"Job Title": "Cybersecurity Specialist", "Avg Salary": "$120,000"},
        {"Job Title": "Cloud Architect", "Avg Salary": "$135,000"},
        {"Job Title": "AI Researcher", "Avg Salary": "$150,000"},
    ]
    df = pd.DataFrame(jobs_data)
    st.dataframe(df)

elif nav_selection == "contact":
    st.subheader("Contact Us")
    st.write("For inquiries, reach out at:")
    st.write("Email: support@nextleap.com")
    st.write("Phone: +1 234 567 890")
    st.write("Website: [NextLeap](https://nextleap.com)")

else:
    # Career Roadmap Generator
    st.subheader("Generate Your Career Roadmap")
    job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")
    submit = st.button("Generate Roadmap")
    
    if submit and job_title:
        input_prompt = f"Provide a professional, step-by-step career roadmap for {job_title}. Include reference URLs if available."
        response = get_hf_response(input_prompt)

        st.subheader("Career Roadmap")
        with st.expander("See Full Details"):
            st.markdown(response.replace("\n", "\n\n"))
        st.success("Roadmap generated successfully.")

    # Learning Resources
    st.subheader("Recommended Courses")
    if job_title:
        courses = get_hf_response(f"List top online courses and learning resources for {job_title}. Include reference URLs if available.")
        st.markdown(courses.replace("\n", "\n\n"))

    # Live Job Listings
    st.subheader("Job Listings")
    if job_title:
        jobs = get_hf_response(f"List top job openings for {job_title} with company names and links.")
        st.markdown(jobs.replace("\n", "\n\n"))
