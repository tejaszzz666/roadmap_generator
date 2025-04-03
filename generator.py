import time
import requests
import streamlit as st
import pandas as pd
from itertools import cycle
from functools import lru_cache
from authlib.integrations.requests_client import OAuth2Session

# Load Google OAuth credentials from Streamlit secrets
GOOGLE_CLIENT_ID = st.secrets["google_oauth"]["client_id"]
GOOGLE_CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]
REDIRECT_URI = st.secrets["google_oauth"]["redirect_uri"]

AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

# Initialize OAuth2 Session
oauth = OAuth2Session(
    GOOGLE_CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    scope=["openid", "email", "profile"]
)

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

# Google OAuth login function
def login_with_google():
    auth_url, state = oauth.create_authorization_url(AUTHORIZATION_URL)
    st.session_state["oauth_state"] = state
    return auth_url

# Handle OAuth callback and fetch user info
def fetch_google_user_info():
    if "oauth_code" in st.query_params:
        token = oauth.fetch_token(
            TOKEN_URL,
            authorization_response=st.query_params["oauth_code"],
            client_secret=GOOGLE_CLIENT_SECRET
        )
        user_info = requests.get(USER_INFO_URL, headers={"Authorization": f"Bearer {token['access_token']}"}).json()
        st.session_state["user_info"] = user_info

# Streamlit UI
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")

# Ferrari-Themed Styling
st.markdown(
    """
    <style>
    body {background-color: #000000; color: white; font-family: 'Arial', sans-serif;}
    .stTextInput > div > div > input {
        border: 2px solid red;
        border-radius: 10px;
        background-color: #1c1c1c;
        color: white;
        padding: 10px;
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: bold;
        background: red;
        color: white;
        padding: 10px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background: yellow;
        color: black;
    }
    h1 {
        text-align: center;
        font-size: 50px;
        color: red;
        font-weight: bold;
    }
    .stTabs {
        background-color: #1c1c1c;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True
)

# Authentication UI
st.sidebar.title("🔐 Login")
if "user_info" not in st.session_state:
    auth_url = login_with_google()
    st.sidebar.markdown(f"[Login with Google]({auth_url})")
else:
    user = st.session_state["user_info"]
    st.sidebar.image(user["picture"], width=50)
    st.sidebar.success(f"Welcome, {user['name']}! 👋")
    st.sidebar.write(f"📧 {user['email']}")

    # ---- Main UI ----
    st.markdown("<h1>NextLeap: Career Roadmap Generator</h1>", unsafe_allow_html=True)
    st.write("Get a structured career roadmap with learning resources tailored to your job title.")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🏁 Career Roadmap", "📚 Resources", "💼 Job Listings"])

    with tab1:
        job_title = st.text_input("Enter the job title:", key="job_title", placeholder="e.g., Data Scientist")
        submit = st.button("Generate Roadmap")
        
        if submit and job_title:
            input_prompt = f"Provide a professional, step-by-step career roadmap for {job_title}. Include reference URLs if available."
            response = get_hf_response(input_prompt)

            st.subheader("Career Roadmap")
            with st.expander("See Full Details"):
                st.markdown(response.replace("\n", "\n\n"))
            st.success("Roadmap generated successfully. ✅")

    with tab2:
        if job_title:
            st.subheader("🏎️ Recommended Courses")
            courses = get_hf_response(f"List top online courses and learning resources for {job_title}. Include reference URLs if available.")
            st.markdown(courses.replace("\n", "\n\n"))
        else:
            st.write("Enter a job title to see recommended courses.")

    with tab3:
        if job_title:
            st.subheader("🏆 Live Job Listings")
            jobs = get_hf_response(f"List top job openings for {job_title} with company names and links.")
            st.markdown(jobs.replace("\n", "\n\n"))
        else:
            st.write("Enter a job title to see job listings.")
