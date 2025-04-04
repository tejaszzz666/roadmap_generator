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

if nav_selection == "Pre-Generated Roadmaps":
    st.title("Pre-Generated Career Roadmaps")
    pre_generated = {
        "Data Scientist": {"roadmap": "1. Learn Python, SQL, and R\n2. Study Data Analysis & Visualization\n3. Master ML & Deep Learning\n4. Work on Real-world Projects\n5. Get Certified (Google, IBM, etc.)\n6. Apply for Data Science Jobs", "url": "https://www.coursera.org/specializations/data-science"},
        "Software Engineer": {"roadmap": "1. Learn Programming (Python, Java, C++)\n2. Study DSA & Competitive Coding\n3. Build Real-world Projects\n4. Master System Design & Databases\n5. Contribute to Open Source\n6. Apply for Tech Jobs", "url": "https://roadmap.sh/software-engineer"},
        "Cybersecurity Expert": {"roadmap": "1. Learn Networking & Security Basics\n2. Get Certified (CEH, CISSP, OSCP)\n3. Learn Ethical Hacking\n4. Master Threat Analysis & Pentesting\n5. Gain Hands-on Experience\n6. Apply for Cybersecurity Roles", "url": "https://www.cybrary.it/"},
        "AI Engineer": {"roadmap": "1. Learn Python & AI Frameworks\n2. Master ML & Neural Networks\n3. Work on AI Projects & Research\n4. Understand Model Deployment\n5. Learn Cloud Platforms (AWS, GCP)\n6. Apply for AI Engineer Jobs", "url": "https://www.deeplearning.ai"},
        "Product Manager": {"roadmap": "1. Learn Business & Market Analysis\n2. Develop Leadership & UX Knowledge\n3. Understand Agile & Scrum\n4. Build Product Roadmaps\n5. Gain Practical Experience\n6. Apply for Product Manager Roles", "url": "https://www.productschool.com/"},
        "Cloud Engineer": {"roadmap": "1. Learn Cloud Platforms (AWS, Azure, GCP)\n2. Get Certified (AWS, Azure, GCP Certs)\n3. Study DevOps & Kubernetes\n4. Master CI/CD Pipelines\n5. Work on Cloud Projects\n6. Apply for Cloud Engineering Jobs", "url": "https://cloud.google.com/training"}
    }
    
    for job, details in pre_generated.items():
        st.subheader(job)
        st.markdown(details["roadmap"].replace("\n", "\n\n"))
        st.markdown(f"[Reference: {job} Roadmap]({details['url']})")
        st.markdown("---")

elif nav_selection == "Best Earning Jobs":
    st.title("Best Earning Jobs & Salaries")
    jobs_data = [
        {"Job Title": "Machine Learning Engineer", "Avg Salary (USD)": "$130,000", "Avg Salary (INR)": "₹1.1 Crore"},
        {"Job Title": "Blockchain Developer", "Avg Salary (USD)": "$140,000", "Avg Salary (INR)": "₹1.2 Crore"},
        {"Job Title": "Cybersecurity Specialist", "Avg Salary (USD)": "$120,000", "Avg Salary (INR)": "₹99 Lakh"},
        {"Job Title": "Cloud Architect", "Avg Salary (USD)": "$135,000", "Avg Salary (INR)": "₹1.15 Crore"},
        {"Job Title": "AI Researcher", "Avg Salary (USD)": "$150,000", "Avg Salary (INR)": "₹1.25 Crore"},
        {"Job Title": "DevOps Engineer", "Avg Salary (USD)": "$125,000", "Avg Salary (INR)": "₹1.05 Crore"},
    ]
    df = pd.DataFrame(jobs_data)
    st.dataframe(df)

elif nav_selection == "Contact":
    st.title("Contact Us")
    st.write("For inquiries, reach out at:")
    st.write("Email: support@nextleap.com")
    st.write("Phone: +1 234 567 890")
    st.write("Website: [NextLeap](https://nextleap.com)")

elif nav_selection == "Videos":
    st.title("Career Guidance Videos")
    st.video("https://www.youtube.com/watch?v=video1")
    st.video("https://www.youtube.com/watch?v=video2")
    st.video("https://www.youtube.com/watch?v=video3")
    st.video("https://www.youtube.com/watch?v=video4")
