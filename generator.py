import time
import requests
import streamlit as st
import pandas as pd
from itertools import cycle
from functools import lru_cache

# Load Hugging Face API keys securely from Streamlit secrets
hf_api_keys = [
    st.secrets["huggingface"]["HF_API_KEY_1"],
    st.secrets["huggingface"]["HF_API_KEY_2"],
    st.secrets["huggingface"]["HF_API_KEY_3"],
    st.secrets["huggingface"]["HF_API_KEY_4"],
    st.secrets["huggingface"]["HF_API_KEY_5"]
]
api_key_cycle = cycle(hf_api_keys)

# Set a reliable, free, big-response model
DEFAULT_MODEL = "tiiuae/falcon-7b-instruct"

@lru_cache(maxsize=50)
def get_hf_response(prompt, model_id=DEFAULT_MODEL):
    """Fetch AI-generated responses from Hugging Face API, rotating keys on errors."""
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers_template = lambda key: {"Authorization": f"Bearer {key}"}

    for _ in range(len(hf_api_keys)):
        api_key = next(api_key_cycle)
        headers = headers_template(api_key)

        try:
            response = requests.post(api_url, headers=headers, json={"inputs": prompt})

            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 10))
                st.warning(f"Rate limited. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            elif response.status_code == 402:
                continue  # Silent skip if quota exceeded
            elif response.status_code == 401:
                continue  # Skip invalid keys

            response.raise_for_status()
            response_data = response.json()

            if isinstance(response_data, list) and 'generated_text' in response_data[0]:
                output = response_data[0]['generated_text']
                if output.startswith(prompt):
                    output = output[len(prompt):].strip()
                return output
            elif isinstance(response_data, dict) and 'generated_text' in response_data:
                return response_data['generated_text']
            else:
                continue

        except Exception as e:
            st.warning(f"Error with key {api_key[:5]}... — {e}")
            continue

    return "❌ All API keys failed or quota exhausted."

# Streamlit UI
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")

st.sidebar.title("Navigation")
nav_selection = st.sidebar.radio("Go to:", ["Home", "Pre-Generated Roadmaps", "Best Earning Jobs", "Contact"])

if nav_selection == "Pre-Generated Roadmaps":
    st.title("Pre-Generated Career Roadmaps")
    roadmaps = {
        "Data Scientist": {
            "roadmap": "1. Learn Python & SQL\n2. Study Data Analysis\n3. Master ML\n4. Projects\n5. Apply for Jobs",
            "url": "https://www.coursera.org/specializations/data-science"
        },
        "Software Engineer": {
            "roadmap": "1. Learn Programming\n2. DSA\n3. Projects\n4. System Design\n5. Apply",
            "url": "https://roadmap.sh/software-engineer"
        },
        "Cybersecurity Expert": {
            "roadmap": "1. Networking Basics\n2. Certifications\n3. Pen Testing\n4. Experience\n5. Apply",
            "url": "https://www.cybrary.it/"
        },
        "AI Engineer": {
            "roadmap": "1. Python + DL\n2. ML & Neural Nets\n3. Projects\n4. Cloud\n5. Apply",
            "url": "https://www.deeplearning.ai"
        },
        "Product Manager": {
            "roadmap": "1. Business Analysis\n2. UX + Agile\n3. Roadmaps\n4. Projects\n5. Apply",
            "url": "https://www.productschool.com/"
        },
        "Cloud Engineer": {
            "roadmap": "1. Learn AWS/GCP\n2. DevOps\n3. Certs\n4. Infra as Code\n5. Apply",
            "url": "https://cloud.google.com/training"
        }
    }

    for role, content in roadmaps.items():
        st.subheader(role)
        st.markdown(content["roadmap"].replace("\n", "\n\n"))
        st.markdown(f"[Learn more]({content['url']})")
        st.markdown("---")

elif nav_selection == "Best Earning Jobs":
    st.title("Top Paying Tech Jobs (India)")
    df = pd.DataFrame([
        {"Job": "Machine Learning Engineer", "Salary": "₹1.08 Cr"},
        {"Job": "Blockchain Developer", "Salary": "₹1.12 Cr"},
        {"Job": "Cybersecurity Specialist", "Salary": "₹96 LPA"},
        {"Job": "Cloud Architect", "Salary": "₹1.05 Cr"},
        {"Job": "AI Researcher", "Salary": "₹1.20 Cr"}
    ])
    st.dataframe(df)

elif nav_selection == "Contact":
    st.title("Contact Us")
    st.write("For inquiries, email:")
    st.write("**support@nextleap.com**")
    st.markdown("[Visit Website](https://roadmapgenerator-x3jmrdqlpa6awk6wambbxv.streamlit.app)")

else:
    st.title("NextLeap : Career Roadmap Generator")
    st.write("Get a structured career roadmap, courses, jobs, and more!")

    job_title = st.text_input("Enter your desired job role:", placeholder="e.g. Cloud Engineer")
    submit = st.button("Generate Career Roadmap")

    if submit and job_title:
        input_prompt = f"Provide a professional, step-by-step career roadmap for a {job_title}. Include helpful URLs and certifications."
        roadmap = get_hf_response(input_prompt)

        st.subheader("Career Roadmap")
        with st.expander("See Full Roadmap"):
            st.markdown(roadmap.replace("\n", "\n\n"))
        st.success("Roadmap generated successfully!")

        st.markdown("---")
        st.subheader("Recommended Courses")
        course_prompt = f"List the best online courses for becoming a {job_title}."
        st.markdown(get_hf_response(course_prompt).replace("\n", "\n\n"))

        st.markdown("---")
        st.subheader("Top Job Openings")
        job_prompt = f"List top job openings for {job_title} in India."
        st.markdown(get_hf_response(job_prompt).replace("\n", "\n\n"))

        st.markdown("---")
        st.subheader("Helpful YouTube Videos")
        yt_prompt = f"List best YouTube videos for {job_title} career guidance."
        st.markdown(get_hf_response(yt_prompt).replace("\n", "\n\n"))