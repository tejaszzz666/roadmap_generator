import time
import requests
import streamlit as st
import pandas as pd

# Streamlit UI setup
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
nav_selection = st.sidebar.radio("Go to:", ["Home", "Pre-Generated Roadmaps", "Best Earning Jobs", "Contact"])

# Shared Together.ai response handler
def get_togetherai_response(question, api_key, model_id="togetherai/career-roadmap-model"):
    if not api_key:
        return "❌ Please enter a valid Together.ai API key."

    api_url = f"https://api.together.ai/v1/models/{model_id}/predict"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.post(api_url, headers=headers, json={"inputs": question})

        if response.status_code == 429:
            wait_time = int(response.headers.get("Retry-After", 10))
            st.warning(f"Rate limit hit. Retrying in {wait_time}s...")
            time.sleep(wait_time)
            return get_togetherai_response(question, api_key, model_id)

        elif response.status_code == 402:
            return "❌ Payment required for using the model."

        response.raise_for_status()
        data = response.json()

        # Assuming the response contains the 'generated_text'
        if "generated_text" in data:
            return data["generated_text"]
        else:
            return "❌ Unexpected response format."

    except requests.exceptions.RequestException as e:
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
    api_key = st.text_input("Enter your Together.ai API Key:", type="password")

    tab1, tab2, tab3, tab4 = st.tabs(["Career Roadmap", "Recommended Courses", "Live Job Listings", "Videos"])

    with tab1:
        job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")
        submit = st.button("Generate Roadmap")

        if submit and job_title and api_key:
            input_prompt = f"Provide a professional, step-by-step career roadmap for {job_title}. Include reference URLs if available."
            response = get_togetherai_response(input_prompt, api_key)
            st.subheader("Career Roadmap")
            with st.expander("See Full Details"):
                st.markdown(response.replace("\n", "\n\n"))
            st.success("Roadmap generated successfully.")
        elif submit and not api_key:
            st.error("Please enter your Together.ai API key.")

    with tab2:
        if submit and job_title and api_key:
            courses = get_togetherai_response(f"List top online courses for {job_title}.", api_key)
            st.markdown(courses.replace("\n", "\n\n"))

    with tab3:
        if submit and job_title and api_key:
            jobs = get_togetherai_response(f"List top job openings for {job_title}.", api_key)
            st.markdown(jobs.replace("\n", "\n\n"))

    with tab4:
        if submit and job_title and api_key:
            videos = get_togetherai_response(f"List top YouTube videos for {job_title} career guidance.", api_key)
            st.markdown(videos.replace("\n", "\n\n"))