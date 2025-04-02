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
                st.warning(f"🚦 Rate limit hit! Retrying in {wait_time} seconds...")
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

    return "❌ Error: All API keys exhausted or failed to respond."

# ✅ CACHE API RESULTS FOR 1 HOUR
@st.cache_data(ttl=3600)  # Cache results for 1 hour
def get_cached_hf_response(question):
    return get_hf_response(question)

# ✅ CUSTOM STYLING & THEMING
st.set_page_config(page_title="Reconnect - Career Guide", page_icon="🚀", layout="wide")

st.markdown(
    """
    <style>
    /* Background */
    .stApp {
        background-color: #F4F6F9;
    }

    /* Title */
    .title {
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        color: #333333;
    }

    /* Input Box */
    .stTextInput>div>div>input {
        font-size: 18px;
        border-radius: 10px;
        padding: 12px;
        border: 2px solid #4CAF50;
        transition: 0.3s;
    }
    .stTextInput>div>div>input:focus {
        border: 2px solid #2E7D32;
        box-shadow: 0px 0px 8px #2E7D32;
    }

    /* Button */
    .stButton>button {
        background: linear-gradient(to right, #4CAF50, #2E7D32);
        color: white;
        font-size: 18px;
        border-radius: 12px;
        padding: 12px 24px;
        transition: 0.3s;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #2E7D32, #4CAF50);
        transform: scale(1.05);
    }

    /* Response Box */
    .response-box {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ UI HEADER
st.markdown("<p class='title'>NEXTLEAP : Career Roadmap Generator</p>", unsafe_allow_html=True)
st.markdown("🔹 Get a **personalized career roadmap** with expert guidance!")

st.divider()

# ✅ USER INPUT
job_title = st.text_input("🔍 Enter the job title:", key="job_title")

# ✅ GENERATE BUTTON WITH SMOOTH ANIMATION
submit = st.button("Generate Roadmap")

if submit:
    full_prompt = f"You are a career guide. Provide a roadmap for: {job_title}."

    with st.spinner("🔄 Generating career roadmap... Please wait."):
        response = get_cached_hf_response(full_prompt)

    # ✅ DISPLAY OUTPUT IN A STYLISH BOX
    st.subheader("Your Career Roadmap")
    with st.container():
        st.markdown(f"<div class='response-box'><p>{response}</p></div>", unsafe_allow_html=True)

    st.success("Roadmap Generated! Keep Learning & Growing")
