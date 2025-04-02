import time
import requests
import streamlit as st
from itertools import cycle

# Load Hugging Face API keys from Streamlit secrets
hf_api_keys = [
    st.secrets["huggingface"]["HF_API_KEY_1"],
    st.secrets["huggingface"]["HF_API_KEY_2"],
    st.secrets["huggingface"]["HF_API_KEY_3"]
]
api_key_cycle = cycle(hf_api_keys)

# Function to get response from Hugging Face model with rate limiting
def get_hf_response(question, model_id="HuggingFaceH4/zephyr-7b-beta"):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"

    for _ in range(len(hf_api_keys)):
        api_key = next(api_key_cycle)
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            response = requests.post(api_url, headers=headers, json={"inputs": question})

            # If rate limited, wait and retry
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 10))  # Default wait: 10 sec
                st.warning(f"Rate limit hit. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue  # Try next key

            response.raise_for_status()
            response_data = response.json()

            if isinstance(response_data, list) and 'generated_text' in response_data[0]:
                return response_data[0]['generated_text']
            else:
                return f"Unexpected response format: {response_data}"

        except requests.exceptions.RequestException as e:
            return f"API Error: {e}"

    return "Error: All API keys exhausted or failed to respond."

# Streamlit Setup
st.set_page_config(page_title="Reconnect - Career Guide", layout="wide")

# Custom CSS for a modern design
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: white;
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #1f1c2c 0%, #928dab 100%);
        padding: 20px;
        border-radius: 20px;
    }
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 12px;
        color: white;
    }
    .stButton>button {
        background: linear-gradient(90deg, #ff7eb3 0%, #ff758c 100%);
        color: white;
        font-size: 18px;
        border-radius: 12px;
        padding: 12px;
        transition: 0.3s ease-in-out;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #ff758c 0%, #ff7eb3 100%);
        transform: scale(1.05);
    }
    .stExpander {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 10px;
    }
    .title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        color: white;
    }
    .sidebar-title {
        font-size: 24px;
        font-weight: bold;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown("<h2 class='sidebar-title'>Navigation</h2>", unsafe_allow_html=True)
page = st.sidebar.radio("Go to", ["Home", "Generate Roadmap", "About", "Contact"])

if page == "Home":
    st.markdown('<h1 class="title">Welcome to NextLeap</h1>', unsafe_allow_html=True)
    st.write("An AI-powered career roadmap generator to help you navigate your journey.")
    st.image("https://source.unsplash.com/1600x900/?career,success", use_column_width=True)

elif page == "Generate Roadmap":
    st.markdown('<h1 class="title">Career Roadmap Generator</h1>', unsafe_allow_html=True)
    st.write("Get a structured career roadmap with learning resources tailored to your job title.")
    job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")
    submit = st.button("Generate Roadmap")
    if submit:
        full_prompt = f"You are a career guide. Provide a roadmap for: {job_title}."
        response = get_hf_response(full_prompt)
        st.subheader("Career Roadmap")
        with st.expander("See Full Details"):
            st.write(response)
        st.success("Roadmap generated successfully.")

elif page == "About":
    st.markdown('<h1 class="title">About NextLeap</h1>', unsafe_allow_html=True)
    st.write("NextLeap is an AI-powered platform that helps users generate personalized career roadmaps.")
    st.image("https://source.unsplash.com/1600x900/?technology,innovation", use_column_width=True)
    st.markdown("### Why Choose Us?")
    st.write("✔ AI-Powered Insights")
    st.write("✔ Tailored Career Guidance")
    st.write("✔ Easy-to-Use Interface")

elif page == "Contact":
    st.markdown('<h1 class="title">Contact Us</h1>', unsafe_allow_html=True)
    st.write("Have questions? Reach out to us!")
    st.text_input("Your Name", placeholder="Enter your name")
    st.text_input("Your Email", placeholder="Enter your email")
    st.text_area("Message", placeholder="Type your message here")
    if st.button("Send Message"):
        st.success("Thank you! We'll get back to you soon.")
