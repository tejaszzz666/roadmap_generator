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

# Navigation Bar
st.sidebar.title("NextLeap Navigation")
page = st.sidebar.radio("Go to:", ["🏁 Career Roadmap", "📚 Resources", "💼 Best Jobs", "📞 Contact"])

if page == "🏁 Career Roadmap":
    st.title("🏁 Career Roadmap Generator")
    job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")
    submit = st.button("Generate Roadmap")
    
    if submit and job_title:
        input_prompt = f"Provide a professional, step-by-step career roadmap for {job_title}. Include reference URLs if available."
        response = get_hf_response(input_prompt)
        
        st.subheader("Career Roadmap")
        with st.expander("See Full Details"):
            st.markdown(response.replace("\n", "\n\n"))
        st.success("Roadmap generated successfully. ✅")

elif page == "📚 Resources":
    st.title("📚 Learning Resources")
    if job_title:
        courses = get_hf_response(f"List top online courses for {job_title}. Include reference URLs if available.")
        st.markdown(courses.replace("\n", "\n\n"))
    else:
        st.write("Enter a job title to see recommended courses.")

elif page == "💼 Best Jobs":
    st.title("💰 Best Earning Jobs & Salaries")
    jobs_data = [
        {"Job Title": "Machine Learning Engineer", "Avg Salary": "$130,000"},
        {"Job Title": "Blockchain Developer", "Avg Salary": "$140,000"},
        {"Job Title": "Cybersecurity Specialist", "Avg Salary": "$120,000"},
        {"Job Title": "Cloud Architect", "Avg Salary": "$135,000"},
        {"Job Title": "AI Researcher", "Avg Salary": "$150,000"},
    ]
    df = pd.DataFrame(jobs_data)
    st.dataframe(df)

elif page == "📞 Contact":
    st.title("📞 Contact Us")
    st.write("For inquiries, reach out at:")
    st.write("📧 Email: support@nextleap.com")
    st.write("📞 Phone: +1 234 567 890")
    st.write("🌍 Website: [NextLeap](https://nextleap.com)")
