import time
import requests
import streamlit as st
import pandas as pd
from itertools import cycle
from functools import lru_cache

# 🔑 API Key Setup
hf_api_keys = [
    st.secrets["huggingface"]["HF_API_KEY_1"],
    st.secrets["huggingface"]["HF_API_KEY_2"],
    st.secrets["huggingface"]["HF_API_KEY_3"],
    st.secrets["huggingface"]["HF_API_KEY_4"],
    st.secrets["huggingface"]["HF_API_KEY_5"]
]
api_key_cycle = cycle(hf_api_keys)

# 💬 API Request Logic
@lru_cache(maxsize=50)
def get_hf_response(question, model_id="mistralai/Mistral-7B-Instruct-v0.1"):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers_template = lambda key: {"Authorization": f"Bearer {key}"}

    for _ in range(len(hf_api_keys)):
        api_key = next(api_key_cycle)
        headers = headers_template(api_key)
        try:
            response = requests.post(api_url, headers=headers, json={"inputs": question})
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 10))
                time.sleep(wait_time)
                continue
            elif response.status_code == 402:
                continue
            response.raise_for_status()
            response_data = response.json()

            if isinstance(response_data, list) and 'generated_text' in response_data[0]:
                output = response_data[0]['generated_text']
                if output.startswith(question):
                    output = output[len(question):].strip()
                return output
        except requests.exceptions.RequestException:
            continue

    return "❌ All API keys failed or quota exhausted."

# 🧠 Cached Call Wrapper
@st.cache_data(ttl=3600)
def get_cached_response(prompt):
    return get_hf_response(prompt)

# 🌐 UI Start
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")
st.sidebar.title("Navigation")
nav_selection = st.sidebar.radio("Go to:", ["Home", "Pre-Generated Roadmaps", "Best Earning Jobs", "Contact"])

# 🗺 Pre-made Roadmaps Page
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
        "Cybersecurity Expert": {
            "roadmap": "1. Learn Networking and Security Basics\n2. Get Certified (CEH, CISSP, OSCP)\n3. Learn Ethical Hacking and Penetration Testing\n4. Gain Hands-on Experience\n5. Apply for Cybersecurity Roles",
            "url": "https://www.cybrary.it/"
        },
        "AI Engineer": {
            "roadmap": "1. Learn Python and Deep Learning Frameworks\n2. Master Machine Learning & Neural Networks\n3. Work on AI/ML Projects\n4. Understand Model Deployment & Cloud Platforms\n5. Apply for AI Engineer Roles",
            "url": "https://www.deeplearning.ai"
        },
        "Product Manager": {
            "roadmap": "1. Learn Business & Market Analysis\n2. Develop Leadership & UX Knowledge\n3. Understand Agile & Scrum Methodologies\n4. Build Roadmaps & Work on Projects\n5. Apply for Product Manager Roles",
            "url": "https://www.productschool.com/"
        },
        "Cloud Engineer": {
            "roadmap": "1. Learn Cloud Platforms (AWS, Azure, GCP)\n2. Master Networking & Security\n3. Understand DevOps & Infrastructure as Code\n4. Gain Certifications\n5. Apply for Cloud Engineer Roles",
            "url": "https://cloud.google.com/training"
        }
    }

    for job, details in pre_generated.items():
        st.subheader(job)
        st.markdown(details["roadmap"].replace("\n", "\n\n"))
        st.markdown(f"[Reference: {job} Roadmap]({details['url']})")
        st.markdown("---")

# 💰 High Salary Jobs Page
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

# 📞 Contact Page
elif nav_selection == "Contact":
    st.title("Contact Us")
    st.write("For inquiries, reach out at:")
    st.write("Email: support@nextleap.com")
    st.write("Website: [NextLeap](https://roadmapgenerator-x3jmrdqlpa6awk6wambbxv.streamlit.app)")

# 🏠 Home Page — Roadmap Generator
else:
    st.title("NextLeap : Career Roadmap Generator")
    st.write("Get a structured career roadmap with learning resources tailored to your job title.")
    job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")
    submit = st.button("Generate Roadmap")

    if submit and job_title:
        job_title = job_title.strip().lower()
        with st.spinner("Generating roadmap..."):
            roadmap_prompt = f"Provide a professional, step-by-step career roadmap for {job_title}. Include reference URLs if available."
            roadmap = get_cached_response(roadmap_prompt)

        st.subheader("Career Roadmap")
        st.markdown(roadmap.replace("\n", "\n\n"))
        st.success("Roadmap generated successfully.")

        # Now show tabs after roadmap is generated
        tab1, tab2, tab3 = st.tabs(["Recommended Courses", "Live Job Listings", "Videos"])

        with tab1:
            with st.spinner("Fetching courses..."):
                course_prompt = f"List top online courses for {job_title}."
                courses = get_cached_response(course_prompt)
                st.markdown(courses.replace("\n", "\n\n"))

        with tab2:
            with st.spinner("Fetching job listings..."):
                job_prompt = f"List top job openings for {job_title}."
                jobs = get_cached_response(job_prompt)
                st.markdown(jobs.replace("\n", "\n\n"))

        with tab3:
            with st.spinner("Fetching videos..."):
                video_prompt = f"List top YouTube videos for {job_title} career guidance."
                videos = get_cached_response(video_prompt)
                st.markdown(videos.replace("\n", "\n\n"))
