import streamlit as st
import pyrebase
from google.cloud import firestore
import requests
import time
from itertools import cycle
from functools import lru_cache

# Firebase Configuration
firebaseConfig = {
    "apiKey": st.secrets["firebase"]["apiKey"],
    "authDomain": st.secrets["firebase"]["authDomain"],
    "projectId": st.secrets["firebase"]["projectId"],
    "appId": st.secrets["firebase"]["appId"],
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firestore.Client()

# Sidebar: Google Sign-In
st.sidebar.title("Login")
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.sidebar.button("Login with Google"):
    provider = "google.com"
    try:
        user = auth.sign_in_with_popup(provider)  # Google Sign-In
        st.session_state["user"] = user
        st.success(f"Logged in as {user['email']}")
    except Exception as e:
        st.error(f"Login failed: {e}")

if st.sidebar.button("Logout"):
    st.session_state["user"] = None
    st.success("Logged out successfully!")

# Save & Fetch User Data
def save_roadmap(user_email, roadmap_data):
    db.collection("users").document(user_email).set({"roadmap": roadmap_data})

def get_roadmap(user_email):
    doc = db.collection("users").document(user_email).get()
    return doc.to_dict() if doc.exists else None

# Hugging Face API Keys
hf_api_keys = [
    st.secrets["huggingface"]["HF_API_KEY_1"],
    st.secrets["huggingface"]["HF_API_KEY_2"],
    st.secrets["huggingface"]["HF_API_KEY_3"],
    st.secrets["huggingface"]["HF_API_KEY_4"]
]
api_key_cycle = cycle(hf_api_keys)

# Caching API Responses
@lru_cache(maxsize=50)
def get_hf_response(question, model_id="mistralai/Mistral-7B-Instruct-v0.1"):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    for _ in range(len(hf_api_keys)):
        api_key = next(api_key_cycle)
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = requests.post(api_url, headers=headers, json={"inputs": question})
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 10))
                time.sleep(wait_time)
                continue
            response.raise_for_status()
            response_data = response.json()
            if isinstance(response_data, list) and 'generated_text' in response_data[0]:
                return response_data[0]['generated_text']
            else:
                return f"Unexpected response format: {response_data}"
        except requests.exceptions.RequestException as e:
            return f"API Error: {e}"
    return "Error: All API keys exhausted or failed to respond."

# Fetch Jobs from API
def fetch_jobs(query):
    response = requests.get(f"https://api.indeed.com/v2/jobs?q={query}&location=India")
    return response.json()

# Community Forum
st.title("Community Forum")
def post_question(user, question):
    db.collection("forum_posts").add({"user": user, "question": question, "upvotes": 0})

def upvote_question(post_id):
    post_ref = db.collection("forum_posts").document(post_id)
    post_ref.update({"upvotes": firestore.Increment(1)})

# Blog Section
def get_blogs():
    blogs = db.collection("blogs").stream()
    return [{"title": blog.to_dict()["title"], "content": blog.to_dict()["content"]} for blog in blogs]

# Dark Mode & Animations
dark_mode = st.toggle("Dark Mode")
if dark_mode:
    st.markdown("""
    <style>
        body { background-color: black; color: white; }
        .stButton>button { transition: 0.3s; }
        .stButton>button:hover { transform: scale(1.05); }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        body { background-color: white; color: black; }
    </style>
    """, unsafe_allow_html=True)
