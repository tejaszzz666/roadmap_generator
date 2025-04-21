import time
import requests
import streamlit as st
import pandas as pd
from together import Together

# Streamlit UI setup
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
nav_selection = st.sidebar.radio("Go to:", ["Home", "Pre-Generated Roadmaps", "Best Earning Jobs", "Contact"])

# Initialize the Together client
client = Together()

# Shared Together.ai response handler using Llama model
def get_llama_response(question, api_key, model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"):
    if not api_key:
        return "❌ Please enter a valid API key."

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ API error: {e}"

# Page Logic
if nav_selection == "Pre-Generated Roadmaps":
    st.title("Pre-Generated Career Roadmaps")
    pre_generated = {
        "Data Scientist": {
            "roadmap": "1. Learn Python & SQL\n2. Study Data Analysis\n3. Master Machine Learning\n4. Build Projects\n5. Apply for Jobs",
            "url": "https://www.coursera.org/specializations/data-science"
        },
        "Software Engineer": {
            "roadmap": "1. Learn Python/Java\n2. DSA\n3. Build Projects\n4. Learn Databases\n5. Apply for Jobs",
            "url": "https://roadmap.sh/software-engineer"
        },
    }

    for job, details in pre_generated.items():
        st.subheader(job)
        st.markdown(details["roadmap"].replace("\n", "\n\n"))
        st.markdown(f"[View Roadmap]({details['url']})")
        st.markdown("---")

elif nav_selection == "Best Earning Jobs":
    st.title("Best Earning Jobs & Salaries")
    df = pd.DataFrame([
        {"Job Title": "ML Engineer", "Avg Salary": "₹1,08,00,000"},
        {"Job Title": "Blockchain Dev", "Avg Salary": "₹1,12,00,000"},
        {"Job Title": "Cybersecurity Expert", "Avg Salary": "₹96,00,000"},
        {"Job Title": "Cloud Architect", "Avg Salary": "₹1,05,00,000"},
        {"Job Title": "AI Researcher", "Avg Salary": "₹1,20,00,000"},
    ])
    st.dataframe(df)

elif nav_selection == "Contact":
    st.title("Contact Us")
    st.write("Email: support@nextleap.com")
    st.write("Website: NextLeap")

else:
    st.title("NextLeap : Career Roadmap Generator")
    st.write("Get a structured career roadmap with learning resources tailored to your job title.")

    # API Key input JUST BELOW title
    api_key = st.text_input("Enter your API Key:", type="password")

    tab1, tab2, tab3, tab4 = st.tabs(["Career Roadmap", "Recommended Courses", "Live Job Listings", "Videos"])

    with tab1:
        job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")
        submit = st.button("Generate Roadmap")

        if submit and job_title and api_key:
            input_prompt = f"Provide a professional, step-by-step career roadmap for {job_title}. Include reference URLs if available."
            response = get_llama_response(input_prompt, api_key)
            st.subheader("Career Roadmap")
            with st.expander("See Full Details"):
                st.markdown(response.replace("\n", "\n\n"))
            st.success("Roadmap generated successfully.")
        elif submit and not api_key:
            st.error("Please enter your API key.")

    with tab2:
        if submit and job_title and api_key:
            courses = get_llama_response(f"List top online courses for {job_title}.", api_key)
            st.markdown(courses.replace("\n", "\n\n"))

    with tab3:
        if submit and job_title and api_key:
            jobs = get_llama_response(f"List top job openings for {job_title}.", api_key)
            st.markdown(jobs.replace("\n", "\n\n"))

    with tab4:
        if submit and job_title and api_key:
            videos = get_llama_response(f"List top YouTube videos for {job_title} career guidance.", api_key)
            st.markdown(videos.replace("\n", "\n\n"))