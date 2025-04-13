import time
import requests
import streamlit as st
import pandas as pd
from itertools import cycle
from functools import lru_cache

# --- API Setup ---
hf_api_keys = [
    st.secrets["huggingface"]["HF_API_KEY_1"],
    st.secrets["huggingface"]["HF_API_KEY_2"],
    st.secrets["huggingface"]["HF_API_KEY_3"],
    st.secrets["huggingface"]["HF_API_KEY_4"],
    st.secrets["huggingface"]["HF_API_KEY_5"]
]
api_key_cycle = cycle(hf_api_keys)

@lru_cache(maxsize=50)
def get_hf_response(question, model_id="distilgpt2"):
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


# --- Page Setup ---
st.set_page_config(page_title="NextLeap - Career Guide", layout="wide")

# --- Custom CSS for Chat UI ---
st.markdown("""
    <style>
    .chat-bubble {
        max-width: 75%;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 10px;
    }
    .user-bubble {
        background-color: #0b93f6;
        color: white;
        align-self: flex-end;
        margin-left: auto;
    }
    .ai-bubble {
        background-color: #e5e5ea;
        color: black;
        align-self: flex-start;
        margin-right: auto;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    </style>
""", unsafe_allow_html=True)


# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
nav_selection = st.sidebar.radio("Go to:", ["Home", "Pre-Generated Roadmaps", "Best Earning Jobs", "Contact"])

# --- Pre-Generated Roadmaps ---
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
        "Cybersecurity Expert": {
            "roadmap": "1. Learn Networking and Security Basics\n2. Get Certified (CEH, CISSP, OSCP)\n3. Learn Ethical Hacking and Penetration Testing\n4. Gain Hands-on Experience\n5. Apply for Cybersecurity Roles",
            "url": "https://www.cybrary.it/"
        },
        "AI Engineer": {
            "roadmap": "1. Learn Python and Deep Learning Frameworks\n2. Master Machine Learning & Neural Networks\n3. Work on AI/ML Projects\n4. Understand Model Deployment & Cloud Platforms\n5. Apply for AI Engineer Roles",
            "url": "https://www.deeplearning.ai"
        },
        "Product Manager": {
            "roadmap": "1. Learn Business & Market Analysis\n2. Develop Leadership & UX Knowledge\n3. Understand Agile & Scrum Methodologies\n4. Build Roadmaps & Work on Projects\n5. Apply for Product Manager Roles",
            "url": "https://www.productschool.com/"
        },
        "Cloud Engineer": {
            "roadmap": "1. Learn Cloud Platforms (AWS, Azure, GCP)\n2. Master Networking & Security\n3. Understand DevOps & Infrastructure as Code\n4. Gain Certifications\n5. Apply for Cloud Engineer Roles",
            "url": "https://cloud.google.com/training"
        }
    }

    for job, details in pre_generated.items():
        st.subheader(job)
        st.markdown(details["roadmap"].replace("\n", "\n\n"))
        st.markdown(f"[Reference: {job} Roadmap]({details['url']})")
        st.markdown("---")


# --- Best Earning Jobs ---
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


# --- Contact Page ---
elif nav_selection == "Contact":
    st.title("Contact Us")
    st.write("For inquiries, reach out at:")
    st.write("Email: support@nextleap.com")
    st.write("Website: [NextLeap](https://roadmapgenerator-x3jmrdqlpa6awk6wambbxv.streamlit.app)")


# --- Home Page with Chat-Style Career Roadmap Generator ---
else:
    st.title("NextLeap : Career Roadmap Generator")
    st.write("Ask any career-related question and get AI-generated roadmaps with learning resources.")

    tab1, tab2, tab3, tab4 = st.tabs(["Career Roadmap (Chat)", "Recommended Courses", "Live Job Listings", "Videos"])

    # --- ChatGPT-style tab ---
    with tab1:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for chat in st.session_state.chat_history:
            role_class = "user-bubble" if chat["role"] == "user" else "ai-bubble"
            st.markdown(f'<div class="chat-bubble {role_class}">{chat["message"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask something career-related:", placeholder="e.g., Roadmap for AI Engineer")
            submitted = st.form_submit_button("Send")

            if submitted and user_input:
                st.session_state.chat_history.append({"role": "user", "message": user_input})
                with st.spinner("Generating roadmap..."):
                    ai_response = get_hf_response(
                        f"Provide a professional, step-by-step career roadmap for {user_input}. Include reference URLs if available."
                    )
                st.session_state.chat_history.append({"role": "assistant", "message": ai_response})

    # --- Additional tabs use similar logic ---
    with tab2:
        if st.session_state.get("chat_history"):
            job_title = st.session_state.chat_history[-1]["message"]
            courses = get_hf_response(f"List top online courses for {job_title}")
            st.subheader("Recommended Courses")
            st.markdown(courses.replace("\n", "\n\n"))
        else:
            st.info("Ask a career-related question in the first tab to get course suggestions.")

    with tab3:
        if st.session_state.get("chat_history"):
            job_title = st.session_state.chat_history[-1]["message"]
            jobs = get_hf_response(f"List top job openings for {job_title}")
            st.subheader("Live Job Listings")
            st.markdown(jobs.replace("\n", "\n\n"))
        else:
            st.info("Ask a career-related question in the first tab to get job suggestions.")

    with tab4:
        if st.session_state.get("chat_history"):
            job_title = st.session_state.chat_history[-1]["message"]
            videos = get_hf_response(f"List top YouTube videos for {job_title} career guidance.")
            st.subheader("Career Videos")
            st.markdown(videos.replace("\n", "\n\n"))
        else:
            st.info("Ask a career-related question in the first tab to get video suggestions.")
