import streamlit as st
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import time
from itertools import cycle
from functools import lru_cache

# 🔹 Firebase Configuration (Fix: Added `databaseURL`)
firebaseConfig = {
    "apiKey": st.secrets["firebase"]["apiKey"],
    "authDomain": st.secrets["firebase"]["authDomain"],
    "databaseURL": st.secrets["firebase"]["databaseURL"],  # ✅ REQUIRED for Pyrebase
    "projectId": st.secrets["firebase"]["projectId"],
    "storageBucket": st.secrets["firebase"]["storageBucket"],
    "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
    "appId": st.secrets["firebase"]["appId"]
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()  # ✅ Pyrebase Realtime Database

# 🔹 Firebase Admin SDK (Firestore Integration)
cred = credentials.Certificate("path/to/serviceAccountKey.json")  # ✅ Add your service account JSON file
firebase_admin.initialize_app(cred)
firestore_db = firestore.client()

# Sidebar: User Authentication
st.sidebar.title("Login")
if "user" not in st.session_state:
    st.session_state["user"] = None

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    try:
        user = auth.sign_in_with_email_and_password(email, password)  # ✅ Correct Pyrebase method
        st.session_state["user"] = user
        st.success(f"Logged in as {user['email']}")
    except Exception as e:
        st.error(f"Login failed: {e}")

if st.sidebar.button("Logout"):
    st.session_state["user"] = None
    st.success("Logged out successfully!")

# 🔹 Save & Fetch User Data
def save_roadmap(user_email, roadmap_data):
    firestore_db.collection("users").document(user_email).set({"roadmap": roadmap_data})  # ✅ Firestore Fix

def get_roadmap(user_email):
    doc = firestore_db.collection("users").document(user_email).get()
    return doc.to_dict() if doc.exists else None

# 🔹 Hugging Face API Keys (Cycle to Bypass Rate Limits)
hf_api_keys = [
    st.secrets["huggingface"]["HF_API_KEY_1"],
    st.secrets["huggingface"]["HF_API_KEY_2"],
    st.secrets["huggingface"]["HF_API_KEY_3"],
    st.secrets["huggingface"]["HF_API_KEY_4"]
]
api_key_cycle = cycle(hf_api_keys)

# 🔹 Caching AI Responses (Optimized Hugging Face API Call)
@lru_cache(maxsize=50)
def get_hf_response(question, model_id="mistralai/Mistral-7B-Instruct-v0.1"):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    for _ in range(len(hf_api_keys)):
        api_key = next(api_key_cycle)
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = requests.post(api_url, headers=headers, json={"inputs": question})
            if response.status_code == 429:  # Rate Limit Handling
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

# 🔹 Fetch Jobs from API (Fix: Corrected API URL)
def fetch_jobs(query):
    api_url = f"https://www.indeed.com/jobs?q={query}&l=India"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to fetch jobs"}

# 🔹 Community Forum
st.title("Community Forum")

def post_question(user, question):
    firestore_db.collection("forum_posts").add({"user": user, "question": question, "upvotes": 0})

def upvote_question(post_id):
    post_ref = firestore_db.collection("forum_posts").document(post_id)
    post_ref.update({"upvotes": firestore.Increment(1)})

# 🔹 Blog Section
def get_blogs():
    blogs = firestore_db.collection("blogs").stream()
    return [{"title": blog.to_dict()["title"], "content": blog.to_dict()["content"]} for blog in blogs]

# 🔹 Dark Mode & Animations (Fix: Improved Styling)
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
