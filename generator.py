import time
import requests
import streamlit as st
import pandas as pd
from functools import lru_cache

# Load Together AI API key from Streamlit secrets
TOGETHER_API_KEY = st.secrets["together_ai"]["API_KEY"]

@lru_cache(maxsize=50)
def get_together_response(prompt, model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"):
    """Fetch response from Together AI API"""
    url = "https://api.together.xyz/v1/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 1024,  # You can reduce this if you want smaller responses
        "temperature": 0.7,
        "stop": ["\nUser:", "\nAssistant:"]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["text"].strip()
    except Exception as e:
        st.error(f"Together AI Error: {e}")
        return "Something went wrong."

# Streamlit UI
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
nav_selection = st.sidebar.radio("Go to:", ["Home", "Pre-Generated Roadmaps", "Best Earning Jobs", "Contact"])

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

elif nav_selection == "Contact":
    st.title("Contact Us")
    st.write("For inquiries, reach out at:")
    st.write("Email: support@nextleap.com")
    st.write("Website: [NextLeap](https://roadmapgenerator-x3jmrdqlpa6awk6wambbxv.streamlit.app)")

else:
    st.title("NextLeap : Career Roadmap Generator")
    st.write("Get a structured career roadmap with learning resources tailored to your job title.")
    tab1, tab2, tab3, tab4 = st.tabs(["Career Roadmap", "Recommended Courses", "Live Job Listings", "Videos"])
    
    with tab1:
        job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")
        submit = st.button("Generate Roadmap")
        
        if submit and job_title:
            input_prompt = f"Provide a professional, step-by-step career roadmap for {job_title}. Include reference URLs if available."
            response = get_together_response(input_prompt)
            st.subheader("Career Roadmap")
            with st.expander("See Full Details"):
                st.markdown(response.replace("\n", "\n\n"))
            st.success("Roadmap generated successfully.")
            
            with tab2:
                courses = get_together_response(f"List top online courses for {job_title}.")
                st.markdown(courses.replace("\n", "\n\n"))
            
            with tab3:
                jobs = get_together_response(f"List top job openings for {job_title}.")            
                st.markdown(jobs.replace("\n", "\n\n"))
            
            with tab4:
                videos = get_together_response(f"List top YouTube videos for {job_title} career guidance.")
                st.markdown(videos.replace("\n", "\n\n"))
