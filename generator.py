import time
import requests
import streamlit as st
import pandas as pd

# Streamlit UI
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")

# API Key input (now comes before job title input)
api_key_input = st.text_input("Enter your Hugging Face API Key:")

def get_hf_response(question, model_id="mistralai/Mixtral-8x7B-Instruct-v0.1"):
    """Fetch AI-generated responses from Hugging Face API."""
    if not api_key_input:
        return "❌ Please enter a valid Hugging Face API key."

    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {api_key_input}"}

    try:
        response = requests.post(api_url, headers=headers, json={"inputs": question})

        if response.status_code == 429:
            wait_time = int(response.headers.get("Retry-After", 10))
            st.warning(f"Rate limit hit. Retrying in {wait_time}s...")
            time.sleep(wait_time)
            return get_hf_response(question, model_id)  # Retry after waiting

        elif response.status_code == 402:
            return "❌ Payment required for using the model."

        response.raise_for_status()
        response_data = response.json()

        if isinstance(response_data, list) and 'generated_text' in response_data[0]:
            output = response_data[0]['generated_text']
            if output.startswith(question):
                output = output[len(question):].strip()
            return output
        else:
            return "❌ Unexpected response format."

    except requests.exceptions.RequestException as e:
        return f"❌ Error with API request: {e}"

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
        # Add other roles as needed
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
    st.write("Website: NextLeap")

else:
    st.title("NextLeap : Career Roadmap Generator")
    st.write("Get a structured career roadmap with learning resources tailored to your job title.")
    tab1, tab2, tab3, tab4 = st.tabs(["Career Roadmap", "Recommended Courses", "Live Job Listings", "Videos"])

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

    with tab2:
        if submit and job_title:
            courses = get_hf_response(f"List top online courses for {job_title}.")
            st.markdown(courses.replace("\n", "\n\n"))

    with tab3:
        if submit and job_title:
            jobs = get_hf_response(f"List top job openings for {job_title}.")
            st.markdown(jobs.replace("\n", "\n\n"))

    with tab4:
        if submit and job_title:
            videos = get_hf_response(f"List top YouTube videos for {job_title} career guidance.")
            st.markdown(videos.replace("\n", "\n\n"))