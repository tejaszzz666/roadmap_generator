import time
import requests
import streamlit as st
import pandas as pd
from itertools import cycle
from functools import lru_cache

# --- Load API Keys ---
hf_api_keys = [
    st.secrets["huggingface"]["HF_API_KEY_1"],
    st.secrets["huggingface"]["HF_API_KEY_2"],
    st.secrets["huggingface"]["HF_API_KEY_3"],
    st.secrets["huggingface"]["HF_API_KEY_4"],
    st.secrets["huggingface"]["HF_API_KEY_5"]
]
api_key_cycle = cycle(hf_api_keys)

@lru_cache(maxsize=50)
def get_hf_response(question, model_id="mistralai/Mistral-7B-Instruct-v0.1"):
    """Fetch AI-generated responses from Hugging Face API."""
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers_template = lambda key: {"Authorization": f"Bearer {key}"}
    
    for _ in range(len(hf_api_keys)):
        api_key = next(api_key_cycle)
        headers = headers_template(api_key)

        try:
            response = requests.post(api_url, headers=headers, json={"inputs": question})
            response.raise_for_status()
            response_data = response.json()

            if isinstance(response_data, list) and 'generated_text' in response_data[0]:
                output = response_data[0]['generated_text']
                if output.startswith(question):
                    output = output[len(question):].strip()
                return output
            else:
                st.warning(f"Unexpected response format: {response_data}")
                continue

        except requests.exceptions.RequestException as e:
            st.warning(f"Error with API key: {api_key[:5]}... — {e}")
            continue

    return "❌ All API keys failed or quota exhausted."

# --- Streamlit UI ---
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
nav_selection = st.sidebar.radio("Go to:", ["Home", "Pre-Generated Roadmaps", "Best Earning Jobs", "Contact"])

# Pre-Generated Roadmaps
if nav_selection == "Pre-Generated Roadmaps":
    st.title("Pre-Generated Career Roadmaps")
    pre_generated = {
        "Data Scientist": {
            "roadmap": "1. Learn Python & SQL\n2. Study Data Analysis and Visualization\n3. Master Machine Learning (Scikit-Learn, TensorFlow, PyTorch)\n4. Work on Projects and Kaggle Competitions\n5. Gain Experience & Apply for Jobs",
            "url": "https://www.coursera.org/specializations/data-science"
        },
        "Software Engineer": {
            "roadmap": "1. Learn Programming (Python, Java, C++)\n2. Understand Data Structures and Algorithms\n3. Build Projects and Contribute to Open Source\n4. Master System Design & Databases\n5. Apply for Internships and Jobs",
            "url": "https://roadmap.sh/software-engineer"
        },
        "AI Engineer": {
            "roadmap": "1. Learn Python and Deep Learning Frameworks\n2. Master Machine Learning & Neural Networks\n3. Work on AI/ML Projects\n4. Understand Model Deployment & Cloud Platforms\n5. Apply for AI Engineer Roles",
            "url": "https://www.deeplearning.ai"
        }
    }

    for job, details in pre_generated.items():
        st.subheader(job)
        st.markdown(details["roadmap"].replace("\n", "\n\n"))
        st.markdown(f"[Reference: {job} Roadmap]({details['url']})")
        st.markdown("---")

# Best Earning Jobs
elif nav_selection == "Best Earning Jobs":
    st.title("Best Earning Jobs & Salaries")
    jobs_data = [
        {"Job Title": "Machine Learning Engineer", "Avg Salary": "₹1,08,00,000"},
        {"Job Title": "Blockchain Developer", "Avg Salary": "₹1,12,00,000"},
        {"Job Title": "Cybersecurity Specialist", "Avg Salary": "₹96,00,000"},
        {"Job Title": "Cloud Architect", "Avg Salary": "₹1,05,00,000"},
        {"Job Title": "AI Researcher", "Avg Salary": "₹1,20,00,000"},
    ]
    df = pd.DataFrame(jobs_data)
    st.dataframe(df)

# Contact Page
elif nav_selection == "Contact":
    st.title("Contact Us")
    st.write("For inquiries, reach out at:")
    st.write("Email: support@nextleap.com")
    st.write("Website: [NextLeap](https://roadmapgenerator-x3jmrdqlpa6awk6wambbxv.streamlit.app)")

# Career Roadmap Generator
else:
    st.title("NextLeap : Career Roadmap Generator")
    st.write("Get a structured career roadmap with learning resources tailored to your job title.")
    tab1, tab2, tab3, tab4 = st.tabs(["Career Roadmap", "Skill Assessment", "Recommended Courses", "Live Job Listings"])

    # Tab 1: Career Roadmap Generator
    with tab1:
        job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")
        submit = st.button("Generate Roadmap")
        
        if submit and job_title:
            input_prompt = f"Provide a professional, step-by-step career roadmap for {job_title}. Include reference URLs if available."
            response = get_hf_response(input_prompt)
            st.subheader("Career Roadmap")
            with st.expander("See Full Details"):
                st.markdown(response.replace("\n", "\n\n"))
            st.success("Roadmap generated successfully.")
    
    # Tab 2: Skill Assessment
    with tab2:
        st.subheader("Skill Assessment")
        skill_level = st.radio("How proficient are you in the following skills?", 
                               ["Beginner", "Intermediate", "Advanced"], key="skill_level")
        st.write(f"Your skill level: {skill_level}")
        st.write("This helps us understand your current capabilities and suggests the best resources.")

    # Tab 3: Recommended Courses
    with tab3:
        if job_title:
            courses = get_hf_response(f"List top online courses for {job_title}.")
            st.subheader("Recommended Courses")
            st.markdown(courses.replace("\n", "\n\n"))
    
    # Tab 4: Live Job Listings
    with tab4:
        if job_title:
            jobs = get_hf_response(f"List top job openings for {job_title}.")            
            st.subheader("Live Job Listings")
            st.markdown(jobs.replace("\n", "\n\n"))
